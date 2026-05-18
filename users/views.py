import logging
from datetime import timedelta
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import CustomUser, CompanyProfile, StudentProfile
from .serializers import (
    RegisterSerializer,
    AdminCompanySerializer,
    CompanyProfileSerializer,
    StudentProfileSerializer,
)
from .permissions import IsNotBlacklisted
from drives.models import PlacementDrive
from applications.models import Application
from utils.exceptions import PermissionError, NotFoundError, ValidationError
from utils.responses import error_response, success_response

logger = logging.getLogger(__name__)


class StudentRegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data, context={'role': 'student'})
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"Student registered successfully: user_id={user.id}")
                return success_response(
                    message="Student registered successfully",
                    status_code=status.HTTP_201_CREATED
                )
            logger.warning(f"Student registration failed with errors: {serializer.errors}")
            return error_response(
                "validation_error",
                "Invalid registration data",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error during student registration: {str(e)}", exc_info=True)
            return error_response(
                "internal_error",
                "An error occurred during registration",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompanyRegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data, context={'role': 'company'})
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"Company registered successfully: user_id={user.id}")
                return success_response(
                    message="Company registered successfully",
                    status_code=status.HTTP_201_CREATED
                )
            logger.warning(f"Company registration failed with errors: {serializer.errors}")
            return error_response(
                "validation_error",
                "Invalid registration data",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error during company registration: {str(e)}", exc_info=True)
            return error_response(
                "internal_error",
                "An error occurred during registration",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class ApproveCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            user = request.user

            if not user.is_superuser:
                logger.warning(f"Non-admin user attempted to approve company: user_id={user.id}")
                raise PermissionError("Only admin can approve companies")

            try:
                company = CustomUser.objects.get(pk=pk, role='company')
            except CustomUser.DoesNotExist:
                logger.warning(f"Company approval attempted for non-existent company: company_id={pk}")
                raise NotFoundError("Company not found")

            company.approve(request.user)
            logger.info(f"Company approved successfully: company_id={company.id}, approved_by={user.id}")

            return success_response("Company approved successfully")
        
        except (PermissionError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error approving company: {str(e)}", exc_info=True)
            raise


class PendingCompaniesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not request.user.is_superuser:
                logger.warning(f"Non-admin user attempted to view pending companies: user_id={request.user.id}")
                raise PermissionError("Only admin can view pending companies")

            companies = CustomUser.objects.filter(
                role='company',
                is_approved=False,
            ).select_related('companyprofile').order_by('date_joined')
            
            # Apply pagination
            paginator = PageNumberPagination()
            page = paginator.paginate_queryset(companies, request)
            if page is not None:
                serializer = AdminCompanySerializer(page, many=True)
                logger.info(f"Pending companies retrieved by admin: user_id={request.user.id}, count={len(page)}")
                return paginator.get_paginated_response(serializer.data)
            
            serializer = AdminCompanySerializer(companies, many=True)
            logger.info(f"Pending companies retrieved by admin: user_id={request.user.id}, count={companies.count()}")
            return Response(serializer.data)
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving pending companies: {str(e)}", exc_info=True)
            raise
    
class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != "company":
                logger.warning(f"Non-company user attempted to view company profile: user_id={request.user.id}, role={request.user.role}")
                raise PermissionError("Only company users can view company profile")

            profile = get_object_or_404(CompanyProfile, user=request.user)
            serializer = CompanyProfileSerializer(profile)
            logger.info(f"Company profile retrieved: user_id={request.user.id}")
            return Response(serializer.data)
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving company profile: {str(e)}", exc_info=True)
            raise

    def patch(self, request):
        try:
            if request.user.role != "company":
                logger.warning(f"Non-company user attempted to update company profile: user_id={request.user.id}")
                raise PermissionError("Only company users can update company profile")

            profile = get_object_or_404(CompanyProfile, user=request.user)
            serializer = CompanyProfileSerializer(profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                logger.info(f"Company profile updated successfully: user_id={request.user.id}")
                return success_response("Profile updated successfully")
            
            logger.warning(f"Company profile update failed with errors: user_id={request.user.id}, errors={serializer.errors}")
            return error_response(
                "validation_error",
                "Invalid profile data",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating company profile: {str(e)}", exc_info=True)
            raise


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "role": "admin" if request.user.is_superuser else request.user.role
        })


class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != "company":
                logger.warning(f"Non-company user attempted to access company dashboard: user_id={request.user.id}")
                raise PermissionError("Only company users can access company dashboard")

            PlacementDrive.close_expired()
            drives = PlacementDrive.objects.filter(company=request.user)

            drive_data = []
            for drive in drives:
                applicant_count = Application.objects.filter(drive=drive).count()

                drive_data.append({
                    "id": drive.id,
                    "job_title": drive.job_title,
                    "status": drive.status,
                    "ctc": drive.ctc,
                    "location": drive.location,
                    "job_type": drive.job_type,
                    "openings": drive.openings,
                    "applicants": applicant_count
                })

            logger.info(f"Company dashboard accessed: user_id={request.user.id}, drives_count={drives.count()}")
            
            return Response({
                "company_name": request.user.companyprofile.company_name if hasattr(request.user, "companyprofile") else "",
                "is_approved": request.user.is_approved,
                "total_drives": drives.count(),
                "drives": drive_data
            })
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error accessing company dashboard: {str(e)}", exc_info=True)
            raise


class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get(self, request):
        try:
            if request.user.role != "student":
                logger.warning(f"Non-student user attempted to access student dashboard: user_id={request.user.id}")
                raise PermissionError("Only student users can access student dashboard")

            search = request.query_params.get("search", "").strip()
            deadline_days = request.query_params.get("deadline_days", "").strip()

            PlacementDrive.close_expired()
            approved_drives = PlacementDrive.objects.filter(
                status="approved",
                application_deadline__gte=timezone.localdate(),
            ).select_related("company", "company__companyprofile")

            if search:
                approved_drives = approved_drives.filter(
                    Q(job_title__icontains=search) |
                    Q(job_description__icontains=search) |
                    Q(eligibility_criteria__icontains=search) |
                    Q(company__username__icontains=search) |
                    Q(company__companyprofile__company_name__icontains=search)
                )
                logger.info(f"Student dashboard search: user_id={request.user.id}, search_term={search}")

            if deadline_days:
                try:
                    days = int(deadline_days)
                except ValueError:
                    logger.warning(f"Invalid deadline_days parameter: {deadline_days}")
                    days = None
                if days is not None:
                    approved_drives = approved_drives.filter(
                        application_deadline__lte=timezone.localdate() + timedelta(days=days)
                    )

            applied_drive_ids = Application.objects.filter(
                student=request.user
            ).values_list("drive_id", flat=True)

            drive_data = []

            for drive in approved_drives:
                if drive.id not in applied_drive_ids:
                    company_name = drive.company.companyprofile.company_name if hasattr(drive.company, "companyprofile") else drive.company.username
                    drive_data.append({
                        "id": drive.id,
                        "job_title": drive.job_title,
                        "company": company_name,
                        "company_name": company_name,
                        "deadline": drive.application_deadline,
                        "ctc": drive.ctc,
                        "location": drive.location,
                        "job_type": drive.job_type,
                        "required_skills": list(drive.required_skills.values_list('name', flat=True)),
                        "openings": drive.openings
            })

            # Applications
            applications = Application.objects.filter(student=request.user)

            application_data = []
            for app in applications:
                company_name = app.drive.company.companyprofile.company_name if hasattr(app.drive.company, "companyprofile") else app.drive.company.username
                application_data.append({
                    "drive_id": app.drive.id,
                    "job_title": app.drive.job_title,
                    "company": company_name,
                    "company_name": company_name,
                    "status": app.status,
                    "current_round": app.current_round,
                    "company_notes": app.company_notes
                })

            logger.info(f"Student dashboard accessed: user_id={request.user.id}, available_drives={len(drive_data)}, applications={len(application_data)}")
            
            return Response({
                "available_drives": drive_data,
                "applications": application_data
            })
        
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error accessing student dashboard: {str(e)}", exc_info=True)
            raise


class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get(self, request):
        try:
            if request.user.role != "student":
                logger.warning(f"Non-student user attempted to view student profile: user_id={request.user.id}")
                raise PermissionError("Only student users can view student profile")

            profile = StudentProfile.objects.get(user=request.user)
            serializer = StudentProfileSerializer(profile)
            logger.info(f"Student profile retrieved: user_id={request.user.id}")
            return Response(serializer.data)
        
        except PermissionError:
            raise
        except StudentProfile.DoesNotExist:
            logger.error(f"Student profile not found: user_id={request.user.id}")
            raise NotFoundError("Student profile not found")
        except Exception as e:
            logger.error(f"Unexpected error retrieving student profile: {str(e)}", exc_info=True)
            raise

    def patch(self, request):
        try:
            if request.user.role != "student":
                logger.warning(f"Non-student user attempted to update student profile: user_id={request.user.id}")
                raise PermissionError("Only student users can update student profile")

            profile = StudentProfile.objects.get(user=request.user)
            serializer = StudentProfileSerializer(profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                logger.info(f"Student profile updated successfully: user_id={request.user.id}")
                return success_response("Profile updated successfully")

            logger.warning(f"Student profile update failed with errors: user_id={request.user.id}, errors={serializer.errors}")
            return error_response(
                "validation_error",
                "Invalid profile data",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        except PermissionError:
            raise
        except StudentProfile.DoesNotExist:
            logger.error(f"Student profile not found: user_id={request.user.id}")
            raise NotFoundError("Student profile not found")
        except Exception as e:
            logger.error(f"Unexpected error updating student profile: {str(e)}", exc_info=True)
            raise


class CompanyViewStudentProfile(APIView):
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get(self, request, pk):
        try:
            if request.user.role != "company":
                logger.warning(f"Non-company user attempted to view student profile: user_id={request.user.id}")
                raise PermissionError("Only companies can view student profiles")

            if not Application.objects.filter(student_id=pk, drive__company=request.user).exists():
                logger.warning(f"Company attempted to view unauthorized student profile: company_id={request.user.id}, student_id={pk}")
                raise PermissionError("You can only view students who applied to your drives")

            try:
                profile = StudentProfile.objects.get(user__id=pk)
            except StudentProfile.DoesNotExist:
                logger.warning(f"Student profile not found: student_id={pk}")
                raise NotFoundError("Student not found")

            serializer = StudentProfileSerializer(profile)
            logger.info(f"Student profile viewed by company: company_id={request.user.id}, student_id={pk}")

            return Response(serializer.data)
        
        except (PermissionError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error viewing student profile: {str(e)}", exc_info=True)
            raise


from users.models import DeveloperAPIKey

class DeveloperAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keys = DeveloperAPIKey.objects.filter(user=request.user, is_active=True).order_by('-created_at')
        data = [{
            "id": k.id,
            "name": k.name,
            "key_preview": k.key[:12] + "..." + k.key[-4:],
            "created_at": k.created_at,
            "last_used": k.last_used,
        } for k in keys]
        return Response(data)

    def post(self, request):
        name = request.data.get('name', 'Default Key').strip() or 'Default Key'
        key_str = DeveloperAPIKey.generate_key_string()
        key_obj = DeveloperAPIKey.objects.create(
            user=request.user,
            name=name,
            key=key_str
        )
        return Response({
            "message": "API Key generated successfully. Please copy it now as it will not be displayed again.",
            "id": key_obj.id,
            "name": key_obj.name,
            "key": key_str,
            "created_at": key_obj.created_at
        }, status=201)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Key ID is required."}, status=400)
        try:
            key_obj = DeveloperAPIKey.objects.get(pk=pk, user=request.user)
            key_obj.delete()
            return Response({"message": "API Key revoked successfully."})
        except DeveloperAPIKey.DoesNotExist:
            return Response({"error": "API Key not found or access denied."}, status=404)
