from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from dashboard.views import AdminDashboardStatsView, CompanyDashboardView, PlacementHistoryView

User = get_user_model()

class DashboardPermissionsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        self.student = User.objects.create_user(username="amit", role="student")
        self.company = User.objects.create_user(username="netflix", role="company", is_approved=True)

    def test_admin_dashboard_stats_permission(self):
        view = AdminDashboardStatsView.as_view()
        
        # Superuser succeeds
        request = self.factory.get('/api/admin/dashboard/')
        force_authenticate(request, user=self.admin)
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Student is denied (returns 403 Forbidden)
        request = self.factory.get('/api/admin/dashboard/')
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_dashboard_stats_permission(self):
        view = CompanyDashboardView.as_view()
        
        # Company succeeds
        request = self.factory.get('/api/company/dashboard/stats/')
        force_authenticate(request, user=self.company)
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Student is denied (returns 403 Forbidden)
        request = self.factory.get('/api/company/dashboard/stats/')
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_placement_history_permission(self):
        view = PlacementHistoryView.as_view()
        
        # Student succeeds
        request = self.factory.get('/api/student/placement-history/')
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Company is denied (returns 403 Forbidden)
        request = self.factory.get('/api/student/placement-history/')
        force_authenticate(request, user=self.company)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
