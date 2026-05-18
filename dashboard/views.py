from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from users.models import CustomUser
from drives.models import PlacementDrive
from applications.models import Application
from applications.serializers import PlacementHistorySerializer

from django.shortcuts import render


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_superuser:
            raise PermissionDenied("Only admin can access dashboard stats")

        PlacementDrive.close_expired()
        data = {
            "total_students": CustomUser.objects.filter(role='student').count(),
            "total_companies": CustomUser.objects.filter(role='company').count(),
            "approved_companies": CustomUser.objects.filter(role='company', is_approved=True).count(),
            "total_drives": PlacementDrive.objects.count(),
            "approved_drives": PlacementDrive.objects.filter(status='approved').count(),
            "total_applications": Application.objects.count(),
        }

        return Response(data)


class AdminListModelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("Only admin can view data list")
        
        model_type = request.query_params.get("type")
        if model_type == "students":
            students = CustomUser.objects.filter(role='student').select_related('studentprofile')
            data = []
            for s in students:
                try:
                    profile = s.studentprofile
                    branch = profile.branch if profile else "N/A"
                    cgpa = profile.cgpa if profile else "N/A"
                    skills = ", ".join([skill.name for skill in profile.skills.all()]) if (profile and profile.skills.exists()) else "N/A"
                except Exception:
                    branch = "N/A"
                    cgpa = "N/A"
                    skills = "N/A"
                
                data.append({
                    "id": s.id,
                    "username": s.username,
                    "email": s.email,
                    "branch": branch,
                    "cgpa": cgpa,
                    "skills": skills,
                })
            return Response(data)
            
        elif model_type == "companies":
            companies = CustomUser.objects.filter(role='company').select_related('companyprofile')
            data = []
            for c in companies:
                try:
                    profile = c.companyprofile
                    company_name = profile.company_name if profile else c.username
                    hr_contact = profile.hr_contact if profile else "N/A"
                except Exception:
                    company_name = c.username
                    hr_contact = "N/A"
                
                data.append({
                    "id": c.id,
                    "username": c.username,
                    "email": c.email,
                    "company_name": company_name,
                    "hr_contact": hr_contact,
                    "is_approved": c.is_approved,
                })
            return Response(data)
            
        elif model_type == "drives":
            drives = PlacementDrive.objects.all().select_related('company', 'company__companyprofile')
            data = []
            for d in drives:
                try:
                    profile = d.company.companyprofile
                    company_name = profile.company_name if profile else d.company.username
                except Exception:
                    company_name = d.company.username
                
                data.append({
                    "id": d.id,
                    "job_title": d.job_title,
                    "company_name": company_name,
                    "ctc": d.ctc,
                    "location": d.location,
                    "job_type": d.job_type,
                    "status": d.status,
                    "openings": d.openings,
                })
            return Response(data)
            
        elif model_type == "applications":
            apps = Application.objects.all().select_related('student', 'drive', 'drive__company', 'drive__company__companyprofile')
            data = [{
                "id": a.id,
                "student_name": a.student.username,
                "job_title": a.drive.job_title,
                "company_name": a.drive.company.companyprofile.company_name if hasattr(a.drive.company, "companyprofile") else a.drive.company.username,
                "status": a.status,
                "current_round": a.current_round,
            } for a in apps]
            return Response(data)
            
        return Response({"error": "Invalid type"}, status=400)


class PlacementHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'student':
            raise PermissionDenied("Only students can view placement history")

        PlacementDrive.close_expired()
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
        

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from dashboard.models import Notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        data = [{
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at
        } for n in notifications]
        return Response({"notifications": data, "count": unread_count})

    def post(self, request):
        # Mark all as read
        from dashboard.models import Notification
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"status": "success"})


class SupportQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        if not subject or not message:
            return Response({"error": "Subject and message are required"}, status=400)
        
        from dashboard.models import SupportQuery
        SupportQuery.objects.create(user=request.user, subject=subject, message=message)
        return Response({"status": "success", "message": "Support request submitted successfully"})


class UserSupportQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from dashboard.models import SupportQuery
        queries = SupportQuery.objects.filter(user=request.user)
        data = [{
            "id": q.id,
            "subject": q.subject,
            "message": q.message,
            "admin_reply": q.admin_reply,
            "is_resolved": q.is_resolved,
            "created_at": q.created_at
        } for q in queries]
        return Response(data)


class AdminSupportQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("Only admin can view support queries")
        from dashboard.models import SupportQuery
        
        status = request.query_params.get("status", "unresolved")
        if status == "resolved":
            queries = SupportQuery.objects.filter(is_resolved=True).select_related('user')
        else:
            queries = SupportQuery.objects.filter(is_resolved=False).select_related('user')
            
        data = [{
            "id": q.id,
            "user": q.user.username,
            "email": q.user.email,
            "subject": q.subject,
            "message": q.message,
            "admin_reply": q.admin_reply,
            "is_resolved": q.is_resolved,
            "created_at": q.created_at
        } for q in queries]
        return Response(data)

    def patch(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("Only admin can resolve support queries")
        from dashboard.models import SupportQuery, Notification
        try:
            q = SupportQuery.objects.get(pk=pk)
            reply = request.data.get("reply", "")
            q.is_resolved = True
            q.admin_reply = reply
            q.save()
            
            # Send Notification
            Notification.objects.create(
                user=q.user,
                message=f"Your support ticket '{q.subject}' has been resolved. Reply: {reply}" if reply else f"Your support ticket '{q.subject}' has been resolved."
            )
            return Response({"status": "success"})
        except SupportQuery.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != 'company':
            raise PermissionDenied("Only companies can access this dashboard")

        PlacementDrive.close_expired()
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

def student_placement_history_page(request):
    return render(request, "student_placement_history.html")

def student_analytics_page(request):
    return render(request, "student_analytics.html")

def company_analytics_page(request):
    return render(request, "company_analytics.html")

def admin_analytics_page(request):
    return render(request, "admin_analytics.html")

def temp_populate_db(request):
    secret = request.GET.get("secret")
    if secret != "supersecret123":
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Invalid secret key.")
    
    import populate_db
    try:
        populate_db.populate()
        from django.http import HttpResponse
        return HttpResponse("🚀 Database successfully populated with high-quality sample records!")
    except Exception as e:
        from django.http import HttpResponseServerError
        import traceback
        return HttpResponseServerError(f"Error occurred: {str(e)}<pre>{traceback.format_exc()}</pre>")
