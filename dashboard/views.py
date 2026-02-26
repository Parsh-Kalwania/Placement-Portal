from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from users.models import CustomUser
from drives.models import PlacementDrive
from applications.models import Application

from django.shortcuts import render


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_superuser:
            raise PermissionDenied("Only admin can access dashboard stats")

        data = {
            "total_students": CustomUser.objects.filter(role='student').count(),
            "total_companies": CustomUser.objects.filter(role='company').count(),
            "approved_companies": CustomUser.objects.filter(role='company', is_approved=True).count(),
            "total_drives": PlacementDrive.objects.count(),
            "approved_drives": PlacementDrive.objects.filter(status='approved').count(),
            "total_applications": Application.objects.count(),
        }

        return Response(data)
    
from applications.serializers import PlacementHistorySerializer


class PlacementHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'student':
            raise PermissionDenied("Only students can view placement history")

        placements = Application.objects.filter(
            student=user,
            status='selected'
        ).select_related(
            'drive',
            'drive__company',
            'drive__company__companyprofile'
        )

        serializer = PlacementHistorySerializer(placements, many=True)

        return Response({
            "total_placements": placements.count(),
            "placements": serializer.data
        })
        

class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'company':
            raise PermissionDenied("Only companies can access this dashboard")

        # Drives created by this company
        drives = PlacementDrive.objects.filter(company=user)

        # Applications to this company's drives
        applications = Application.objects.filter(drive__company=user)

        data = {
            "total_drives": drives.count(),
            "pending_drives": drives.filter(status='pending').count(),
            "approved_drives": drives.filter(status='approved').count(),
            "closed_drives": drives.filter(status='closed').count(),

            "total_applications": applications.count(),
            "shortlisted": applications.filter(status='shortlisted').count(),
            "selected": applications.filter(status='selected').count(),
            "rejected": applications.filter(status='rejected').count(),
        }

        return Response(data)
    

def login_view(request):
    return render(request, "login.html")

def student_signup_page(request):
    return render(request, "student_signup.html")

def company_signup_page(request):
    return render(request, "company_signup.html")

def root_view(request):
    return render(request, "root.html")

def dashboard_page(request):
    return render(request, "dashboard.html")

def company_dashboard_page(request):
    return render(request, "company_dashboard.html")

def company_complete_profile_page(request):
    return render(request, "company_complete_profile.html")

def company_edit_profile_page(request):
    return render(request, "company_edit_profile.html")

def student_dashboard_page(request):
    return render(request, "student_dashboard.html")

def admin_dashboard_page(request):
    return render(request, "admin_dashboard.html")

def company_add_drive_page(request):
    return render(request, "company_add_drive.html")

def company_drive_detail_page(request, pk):
    return render(request, "company_drive_detail.html")

def student_drive_detail_page(request, pk):
    return render(request, "student_drive_detail.html")

def student_edit_profile_page(request):
    return render(request, "student_edit_profile.html")

def company_student_profile_page(request, pk):
    return render(request, "company_student_profile.html")