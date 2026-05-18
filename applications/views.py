from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Application
from .serializers import ApplicationSerializer
from users.permissions import IsNotBlacklisted


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    COMPANY_STATUS_CHOICES = {"shortlisted", "selected", "rejected"}

    def get_queryset(self):
        user = self.request.user

        queryset = Application.objects.select_related(
            "student",
            "drive",
            "drive__company",
            "drive__company__companyprofile",
        )

        if user.is_superuser:
            return queryset

        if user.role == "student":
            return queryset.filter(student=user)

        if user.role == "company":
            return queryset.filter(drive__company=user)

        return Application.objects.none()

    def validate_company_can_manage(self, application):
        user = self.request.user
        if user.role != "company" or application.drive.company != user:
            raise PermissionDenied("Only the drive company can update application status")

    def update_application_progress(self, application, status_value):
        self.validate_company_can_manage(application)
        if status_value not in self.COMPANY_STATUS_CHOICES:
            raise PermissionDenied("Invalid application status transition")

        serializer = self.get_serializer(
            application,
            data={
                "status": status_value,
                "current_round": self.request.data.get("current_round", application.current_round),
                "company_notes": self.request.data.get("company_notes", application.company_notes),
            },
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(student=application.student, drive=application.drive)
        
        from dashboard.models import Notification
        msg = f"Your application for {application.drive.job_title} has been updated to {status_value}."
        Notification.objects.create(user=application.student, message=msg)
        
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        from drives.models import PlacementDrive
        PlacementDrive.close_expired()

        if user.role != "student":
            raise PermissionDenied("Only students can apply")

        drive = serializer.validated_data["drive"]

        if drive.status != "approved":
            raise PermissionDenied("You can only apply to approved drives")

        if drive.application_deadline < timezone.localdate():
            raise PermissionDenied("This drive's application deadline has passed")

        from users.models import StudentProfile
        from rest_framework.exceptions import ValidationError
        try:
            profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            raise PermissionDenied("Complete your student profile before applying.")

        if not profile.phone or not profile.branch or profile.cgpa is None:
            raise PermissionDenied("Complete your student profile (phone, branch, and CGPA) before applying.")

        if profile.cgpa < drive.min_cgpa:
            raise ValidationError(f"Your CGPA ({profile.cgpa}) is below the minimum required CGPA ({drive.min_cgpa}) for this drive.")

        if drive.eligible_branches and profile.branch not in drive.eligible_branches:
            raise ValidationError(f"Your branch '{profile.branch}' is not eligible for this drive. Eligible branches: {', '.join(drive.eligible_branches)}")

        # Prevent duplicate applications
        if Application.objects.filter(student=user, drive=drive).exists():
            raise PermissionDenied("You already applied to this drive")

        serializer.save(student=user, status="applied")

    def perform_update(self, serializer):
        application = self.get_object()
        self.validate_company_can_manage(application)

        next_status = serializer.validated_data.get("status", application.status)
        if next_status not in self.COMPANY_STATUS_CHOICES:
            raise PermissionDenied("Companies can only shortlist, select, or reject applicants")

        updated_app = serializer.save(
            student=application.student,
            drive=application.drive,
        )
        
        from dashboard.models import Notification
        msg = f"Your application for {application.drive.job_title} has been updated to {next_status}."
        Notification.objects.create(user=application.student, message=msg)

    @action(detail=True, methods=["patch", "post"])
    def shortlist(self, request, pk=None):
        return self.update_application_progress(self.get_object(), "shortlisted")

    @action(detail=True, methods=["patch", "post"])
    def select(self, request, pk=None):
        return self.update_application_progress(self.get_object(), "selected")

    @action(detail=True, methods=["patch", "post"])
    def reject(self, request, pk=None):
        return self.update_application_progress(self.get_object(), "rejected")
