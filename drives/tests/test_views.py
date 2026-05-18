from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive

User = get_user_model()

class DrivesViewsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        
        self.company = User.objects.create_user(username="netflix", role="company", is_approved=True)
        # Bypassing complete profile check
        profile = self.company.companyprofile
        profile.company_name = "Netflix"
        profile.hr_contact = "9998887776"
        profile.save()

        self.student = User.objects.create_user(username="arun", role="student")
        
        self.drive_data = {
            "job_title": "Software Engineer",
            "job_description": "We need python devs.",
            "eligibility_criteria": "CGPA > 7",
            "application_deadline": timezone.localdate() + timedelta(days=5),
            "ctc": 14.50,
            "openings": 2,
            "required_skills": "Python, Django"
        }

    def test_create_drive_api(self):
        self.client.force_authenticate(user=self.company)
        response = self.client.post("/api/drives/", self.drive_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PlacementDrive.objects.filter(job_title="Software Engineer", company=self.company).exists())

    def test_admin_view_and_approve_drive(self):
        # Create a pending drive
        drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="DevOps Engineer",
            job_description="Infra work",
            eligibility_criteria="AWS knowledge",
            application_deadline=timezone.localdate() + timedelta(days=5),
            status="pending"
        )
        
        self.client.force_authenticate(user=self.admin)
        
        # Test pending list
        pending_response = self.client.get("/api/admin/drives/pending/")
        self.assertEqual(pending_response.status_code, status.HTTP_200_OK)
        
        # Test approve drive
        approve_response = self.client.patch(f"/api/admin/drives/{drive.id}/approve/")
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        drive.refresh_from_db()
        self.assertEqual(drive.status, "approved")

    def test_student_view_drive(self):
        # Approved drive
        drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="Data Scientist",
            job_description="ML work",
            eligibility_criteria="Math",
            application_deadline=timezone.localdate() + timedelta(days=5),
            status="approved"
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f"/api/student/drive/{drive.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["job_title"], "Data Scientist")
