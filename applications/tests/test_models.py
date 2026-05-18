from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive
from applications.models import Application, ApplicationTimeline

User = get_user_model()

class ApplicationModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="amit", role="student")
        self.company = User.objects.create_user(username="netflix", role="company", is_approved=True)
        self.drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="Intern",
            job_description="Description",
            eligibility_criteria="Eligibility",
            application_deadline=timezone.localdate() + timedelta(days=5),
            status="approved"
        )

    def test_create_application_and_timeline(self):
        app = Application.objects.create(
            student=self.student,
            drive=self.drive,
            status="applied"
        )
        self.assertEqual(str(app), "amit - Intern")
        
        timeline = ApplicationTimeline.objects.create(
            application=app,
            stage="Applied",
            notes="Application submitted successfully"
        )
        self.assertEqual(str(timeline), "amit - Intern - Applied")

    def test_unique_student_drive_constraint(self):
        # Create first application
        Application.objects.create(
            student=self.student,
            drive=self.drive
        )
        # Attempt to create duplicate application should fail
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                student=self.student,
                drive=self.drive
            )
