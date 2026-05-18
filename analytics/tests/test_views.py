from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive
from applications.models import Application

User = get_user_model()

class AnalyticsViewsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        
        self.student = User.objects.create_user(username="arun", role="student")
        profile = self.student.studentprofile
        profile.phone = "9876543210"
        profile.branch = "Computer Science"
        profile.cgpa = 9.0
        profile.batch_year = 2026
        profile.save()

        self.company = User.objects.create_user(username="netflix", role="company", is_approved=True)
        self.drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="Software Intern",
            job_description="Description",
            eligibility_criteria="Eligibility",
            application_deadline=timezone.localdate() + timedelta(days=5),
            min_cgpa=8.0,
            eligible_branches=["Computer Science"],
            status="approved"
        )
        # Create application and select it to establish placed student baseline
        self.app = Application.objects.create(
            student=self.student,
            drive=self.drive,
            status="selected"
        )

    def test_student_analytics_calculation(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/student/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check calculation metrics
        self.assertEqual(response.data["total_applications"], 1)
        self.assertEqual(response.data["selected"], 1)
        self.assertEqual(response.data["success_rate"], 100.0)
        self.assertEqual(float(response.data["student_cgpa"]), 9.0)

    def test_student_smart_matches(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/student/smart-matches/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("matches", response.data)
        self.assertTrue(len(response.data["matches"]) >= 0)

    def test_company_analytics_calculation(self):
        self.client.force_authenticate(user=self.company)
        response = self.client.get("/api/company/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check company calculation metrics
        self.assertEqual(response.data["total_drives"], 1)
        self.assertEqual(response.data["total_applicants"], 1)
        self.assertEqual(response.data["selected"], 1)

    def test_admin_analytics_calculation(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/admin/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check admin calculation metrics
        self.assertEqual(response.data["total_students"], 1)  # only student is arun
        self.assertEqual(response.data["placed_students"], 1)
        self.assertEqual(response.data["total_drives"], 1)
