import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import PlacementDrive
from .serializers import PlacementDriveSerializer
from applications.models import Application
from utils.exceptions import PermissionError, NotFoundError, ValidationError
from utils.responses import error_response, success_response

logger = logging.getLogger(__name__)

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
        PlacementDrive.close_expired()

        if user.is_superuser:
            return PlacementDrive.objects.select_related('company', 'company__companyprofile')

        if user.role == 'company':
            return PlacementDrive.objects.filter(company=user).select_related('company', 'company__companyprofile')

        if user.role == 'student':
            return PlacementDrive.objects.filter(
                status='approved',
                application_deadline__gte=timezone.localdate(),
            ).select_related('company', 'company__companyprofile')

        return PlacementDrive.objects.none()

    # 🔹 Restrict who can create/update/delete
    def get_permissions(self):
        return [IsAuthenticated()]

    # 🔹 Only approved companies can create drives
    def perform_create(self, serializer):
        try:
            user = self.request.user

            if user.role != 'company':
                logger.warning(f"Non-company user attempted to create drive: user_id={user.id}, role={user.role}")
                raise PermissionError("Only companies can create drives")

            if not user.is_approved:
                logger.warning(f"Unapproved company attempted to create drive: company_id={user.id}")
                raise PermissionError("Company not approved by admin")

            profile = getattr(user, 'companyprofile', None)
            if not profile or not profile.company_name.strip() or not profile.hr_contact.strip():
                logger.warning(f"Company with incomplete profile attempted to create drive: company_id={user.id}")
                raise PermissionError("Complete your company profile before creating drives")

            drive = serializer.save(company=user)
            logger.info(f"Placement drive created successfully: drive_id={drive.id}, company_id={user.id}, job_title={drive.job_title}")
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating drive: {str(e)}", exc_info=True)
            raise

    # 🔹 Prevent company from editing other company's drive
    def perform_update(self, serializer):
        try:
            drive = self.get_object()
            user = self.request.user

            if not user.is_superuser and drive.company != user:
                logger.warning(f"Unauthorized drive update attempted: user_id={user.id}, drive_id={drive.id}, company_id={drive.company.id}")
                raise PermissionError("You cannot modify this drive")

            updated_drive = serializer.save()
            logger.info(f"Placement drive updated successfully: drive_id={drive.id}, updated_by={user.id}")
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating drive: {str(e)}", exc_info=True)
            raise

    # 🔹 Prevent company from deleting other company's drive
    def perform_destroy(self, instance):
        try:
            user = self.request.user

            if not user.is_superuser and instance.company != user:
                logger.warning(f"Unauthorized drive deletion attempted: user_id={user.id}, drive_id={instance.id}, company_id={instance.company.id}")
                raise PermissionError("You cannot delete this drive")

            logger.info(f"Placement drive deleted: drive_id={instance.id}, deleted_by={user.id}")
            instance.delete()
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting drive: {str(e)}", exc_info=True)
            raise
        
class ApproveDriveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            user = request.user

            if not user.is_superuser:
                logger.warning(f"Non-admin user attempted to approve drive: user_id={user.id}")
                raise PermissionError("Only admin can approve drives")

            try:
                drive = PlacementDrive.objects.get(pk=pk)
            except PlacementDrive.DoesNotExist:
                logger.warning(f"Drive approval attempted for non-existent drive: drive_id={pk}")
                raise NotFoundError("Drive not found")

            drive.status = 'approved'
            drive.save()

            logger.info(f"Placement drive approved: drive_id={drive.id}, approved_by={user.id}, job_title={drive.job_title}")
            return success_response("Drive approved successfully")
        
        except (PermissionError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error approving drive: {str(e)}", exc_info=True)
            raise


class PendingDrivesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not request.user.is_superuser:
                logger.warning(f"Non-admin user attempted to view pending drives: user_id={request.user.id}")
                raise PermissionError("Only admin can view pending drives")

            PlacementDrive.close_expired()
            drives = PlacementDrive.objects.filter(status='pending').select_related(
                'company',
                'company__companyprofile',
            ).order_by('created_at')
            
            # Apply pagination
            paginator = PageNumberPagination()
            page = paginator.paginate_queryset(drives, request)
            if page is not None:
                serializer = PlacementDriveSerializer(page, many=True)
                logger.info(f"Pending drives retrieved by admin: user_id={request.user.id}, count={len(page)}")
                return paginator.get_paginated_response(serializer.data)
            
            serializer = PlacementDriveSerializer(drives, many=True)
            logger.info(f"Pending drives retrieved by admin: user_id={request.user.id}, count={drives.count()}")
            return Response(serializer.data)
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving pending drives: {str(e)}", exc_info=True)
            raise

class CompanyDriveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            if request.user.role != "company":
                logger.warning(f"Non-company user attempted to view company drive detail: user_id={request.user.id}")
                raise PermissionError("Only company users can view company drive detail")

            PlacementDrive.close_expired()
            try:
                drive = PlacementDrive.objects.get(pk=pk, company=request.user)
            except PlacementDrive.DoesNotExist:
                logger.warning(f"Company drive detail not found: drive_id={pk}, company_id={request.user.id}")
                raise NotFoundError("Drive not found")

            applications = Application.objects.filter(drive=drive)

            applicant_data = []
            for app in applications:
                applicant_data.append({
                    "application_id": app.id,
                    "student_id": app.student.id,
                    "student_name": app.student.username,
                    "status": app.status,
                    "current_round": app.current_round,
                    "company_notes": app.company_notes
                })

            logger.info(f"Company drive detail accessed: company_id={request.user.id}, drive_id={drive.id}, applicants={len(applicant_data)}")
            
            return Response({
                "job_title": drive.job_title,
                "status": drive.status,
                "ctc": drive.ctc,
                "location": drive.location,
                "job_type": drive.job_type,
                "required_skills": ", ".join(drive.required_skills.values_list('name', flat=True)),
                "openings": drive.openings,
                "deadline": drive.application_deadline,
                "applications": applicant_data
            })
        
        except (PermissionError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error accessing company drive detail: {str(e)}", exc_info=True)
            raise

class StudentDriveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            if request.user.role != "student":
                logger.warning(f"Non-student user attempted to view student drive detail: user_id={request.user.id}")
                raise PermissionError("Not allowed")

            PlacementDrive.close_expired()
            try:
                drive = PlacementDrive.objects.select_related('company', 'company__companyprofile').get(
                    pk=pk,
                    status="approved",
                    application_deadline__gte=timezone.localdate(),
                )
            except PlacementDrive.DoesNotExist:
                logger.warning(f"Student drive detail not found: drive_id={pk}, student_id={request.user.id}")
                raise NotFoundError("Drive not found")

            company_name = drive.company.companyprofile.company_name if hasattr(drive.company, "companyprofile") else drive.company.username

            logger.info(f"Student drive detail accessed: student_id={request.user.id}, drive_id={drive.id}, company={company_name}")
            
            return Response({
                "job_title": drive.job_title,
                "company": company_name,
                "company_name": company_name,
                "description": drive.job_description,
                "eligibility": drive.eligibility_criteria,
                "deadline": drive.application_deadline,
                "ctc": drive.ctc,
                "location": drive.location,
                "job_type": drive.job_type,
                "required_skills": ", ".join(drive.required_skills.values_list('name', flat=True)),
                "openings": drive.openings
            })
        
        except (PermissionError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error accessing student drive detail: {str(e)}", exc_info=True)
            raise
