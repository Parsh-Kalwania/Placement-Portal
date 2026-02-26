from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import PlacementDrive
from .serializers import PlacementDriveSerializer
from users.permissions import IsCompany

from rest_framework.views import APIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

class PlacementDriveViewSet(ModelViewSet):
    queryset = PlacementDrive.objects.all()
    serializer_class = PlacementDriveSerializer
    permission_classes = [IsAuthenticated]

    # 🔹 Enable filtering + search
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status']
    search_fields = ['job_title', 'job_description']

    # 🔹 Role-based visibility (Base restriction)
    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return PlacementDrive.objects.all()

        if user.role == 'company':
            return PlacementDrive.objects.filter(company=user)

        if user.role == 'student':
            return PlacementDrive.objects.filter(status='approved')

        return PlacementDrive.objects.none()

    # 🔹 Restrict who can create/update/delete
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCompany()]
        return [IsAuthenticated()]

    # 🔹 Only approved companies can create drives
    def perform_create(self, serializer):
        user = self.request.user

        if user.role != 'company':
            raise PermissionDenied("Only companies can create drives")

        if not user.is_approved:
            raise PermissionDenied("Company not approved by admin")

        serializer.save(company=user)

    # 🔹 Prevent company from editing other company's drive
    def perform_update(self, serializer):
        drive = self.get_object()
        user = self.request.user

        if not user.is_superuser and drive.company != user:
            raise PermissionDenied("You cannot modify this drive")

        serializer.save()

    # 🔹 Prevent company from deleting other company's drive
    def perform_destroy(self, instance):
        user = self.request.user

        if not user.is_superuser and instance.company != user:
            raise PermissionDenied("You cannot delete this drive")

        instance.delete()
        
class ApproveDriveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        if not user.is_superuser:
            raise PermissionDenied("Only admin can approve drives")

        try:
            drive = PlacementDrive.objects.get(pk=pk)
        except PlacementDrive.DoesNotExist:
            return Response({"error": "Drive not found"}, status=404)

        drive.status = 'approved'
        drive.save()

        return Response({"message": "Drive approved successfully"})
    
from applications.models import Application

class CompanyDriveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role != "company":
            return Response({"error": "Not allowed"}, status=403)

        try:
            drive = PlacementDrive.objects.get(pk=pk, company=request.user)
        except PlacementDrive.DoesNotExist:
            return Response({"error": "Drive not found"}, status=404)

        applications = Application.objects.filter(drive=drive)

        applicant_data = []
        for app in applications:
            applicant_data.append({
                "application_id": app.id,
                "student_id": app.student.id,
                "student_name": app.student.username,
                "status": app.status
            })

        return Response({
            "job_title": drive.job_title,
            "status": drive.status,
            "applications": applicant_data
        })
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class StudentDriveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if request.user.role != "student":
            raise PermissionDenied("Not allowed")

        try:
            drive = PlacementDrive.objects.get(pk=pk, status="approved")
        except PlacementDrive.DoesNotExist:
            return Response({"error": "Drive not found"}, status=404)

        return Response({
            "job_title": drive.job_title,
            "company": drive.company.username,
            "description": drive.job_description,
            "eligibility": drive.eligibility_criteria,
            "deadline": drive.application_deadline
        })