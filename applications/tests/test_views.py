from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive
from applications.models import Application

User = get_user_model()

class ApplicationViewsTestCase(APITestCase):
    def setUp(self):
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
            job_title="Intern",
            job_description="Cool job",
            eligibility_criteria="CGPA > 7",
            application_deadline=timezone.localdate() + timedelta(days=5),
            min_cgpa=8.0,
            eligible_branches=["Computer Science"],
            status="approved"
        )

    def test_apply_to_drive(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/api/applications/", {"drive": self.drive.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Application.objects.filter(student=self.student, drive=self.drive).exists())

    def test_company_view_and_update_application_status(self):
        # Create application first
        app = Application.objects.create(
            student=self.student,
            drive=self.drive,
            status="applied"
        )
        
        # Authenticate company
        self.client.force_authenticate(user=self.company)
        
        # Test company can view candidates for their drive
        list_response = self.client.get("/api/applications/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        
        # Test company can shortlist candidate
        update_response = self.client.patch(f"/api/applications/{app.id}/", {
            "status": "shortlisted",
            "current_round": "Technical Round 1",
            "company_notes": "Impressive resume"
        }, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        app.refresh_from_db()
        self.assertEqual(app.status, "shortlisted")
        self.assertEqual(app.current_round, "Technical Round 1")
