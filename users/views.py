from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser
from django.shortcuts import get_object_or_404

from .models import CompanyProfile
from .serializers import CompanyProfileSerializer


class StudentRegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'role': 'student'})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyRegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'role': 'company'})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApproveCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        if not user.is_superuser:
            raise PermissionDenied("Only admin can approve companies")

        try:
            company = CustomUser.objects.get(pk=pk, role='company')
        except CustomUser.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)

        company.is_approved = True
        company.save()

        return Response({"message": "Company approved successfully"})
    
class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "company":
            return Response({"error": "Not allowed"}, status=403)

        profile = get_object_or_404(CompanyProfile, user=request.user)
        serializer = CompanyProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        if request.user.role != "company":
            return Response({"error": "Not allowed"}, status=403)

        profile = get_object_or_404(CompanyProfile, user=request.user)
        serializer = CompanyProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})
        return Response(serializer.errors, status=400)
    
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "role": request.user.role
        })
        

from drives.models import PlacementDrive
from applications.models import Application

class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "company":
            return Response({"error": "Not allowed"}, status=403)

        drives = PlacementDrive.objects.filter(company=request.user)

        drive_data = []
        for drive in drives:
            applicant_count = Application.objects.filter(drive=drive).count()

            drive_data.append({
                "id": drive.id,
                "job_title": drive.job_title,
                "status": drive.status,
                "applicants": applicant_count
            })

        return Response({
            "company_name": request.user.companyprofile.company_name if hasattr(request.user, "companyprofile") else "",
            "is_approved": request.user.is_approved,
            "total_drives": drives.count(),
            "drives": drive_data
        })
        
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drives.models import PlacementDrive
from applications.models import Application


class StudentDashboardView(APIView):
    from users.permissions import IsNotBlacklisted

    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get(self, request):
        if request.user.role != "student":
            return Response({"error": "Not allowed"}, status=403)

        # Approved drives
        approved_drives = PlacementDrive.objects.filter(status="approved")

        applied_drive_ids = Application.objects.filter(
            student=request.user
        ).values_list("drive_id", flat=True)

        drive_data = []

        for drive in approved_drives:
            if drive.id not in applied_drive_ids:
                drive_data.append({
                    "id": drive.id,
                    "job_title": drive.job_title,
                    "company": drive.company.username,
                    "deadline": drive.application_deadline
        })

        # Applications
        applications = Application.objects.filter(student=request.user)

        application_data = []
        for app in applications:
            application_data.append({
                "drive_id": app.drive.id,
                "job_title": app.drive.job_title,
                "company": app.drive.company.username,
                "status": app.status
            })

        return Response({
            "available_drives": drive_data,
            "applications": application_data
        })
        
from .models import StudentProfile
from .serializers import StudentProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsNotBlacklisted


class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get(self, request):
        if request.user.role != "student":
            return Response({"error": "Not allowed"}, status=403)

        profile = StudentProfile.objects.get(user=request.user)
        serializer = StudentProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        if request.user.role != "student":
            return Response({"error": "Not allowed"}, status=403)

        profile = StudentProfile.objects.get(user=request.user)
        serializer = StudentProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})

        return Response(serializer.errors, status=400)
    
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from users.permissions import IsNotBlacklisted
from .models import StudentProfile
from .serializers import StudentProfileSerializer


class CompanyViewStudentProfile(APIView):
    permission_classes = [IsAuthenticated, IsNotBlacklisted]

    def get(self, request, pk):

        if request.user.role != "company":
            raise PermissionDenied("Only companies can view student profiles")

        try:
            profile = StudentProfile.objects.get(user__id=pk)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        serializer = StudentProfileSerializer(profile)

        return Response(serializer.data)