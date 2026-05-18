from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from analytics.views import StudentAnalyticsView, CompanyAnalyticsView, AdminAnalyticsView

User = get_user_model()

class AnalyticsPermissionsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        self.student = User.objects.create_user(username="amit", role="student")
        self.company = User.objects.create_user(username="netflix", role="company", is_approved=True)

    def test_student_analytics_permission(self):
        view = StudentAnalyticsView.as_view()
        
        # Student succeeds
        request = self.factory.get('/api/student/analytics/')
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Company is denied (returns 403 Forbidden)
        request = self.factory.get('/api/student/analytics/')
        force_authenticate(request, user=self.company)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_analytics_permission(self):
        view = CompanyAnalyticsView.as_view()
        
        # Company succeeds
        request = self.factory.get('/api/company/analytics/')
        force_authenticate(request, user=self.company)
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Student is denied (returns 403 Forbidden)
        request = self.factory.get('/api/company/analytics/')
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_analytics_permission(self):
        view = AdminAnalyticsView.as_view()
        
        # Admin succeeds
        request = self.factory.get('/api/admin/analytics/')
        force_authenticate(request, user=self.admin)
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Student is denied (returns 403 Forbidden)
        request = self.factory.get('/api/admin/analytics/')
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
