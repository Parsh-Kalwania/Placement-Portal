from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive
from applications.models import Application
from applications.serializers import ApplicationSerializer, PlacementHistorySerializer

User = get_user_model()

class ApplicationSerializerTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="rohan", role="student")
        self.company = User.objects.create_user(username="netflix", role="company", is_approved=True)
        self.drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="Intern",
            job_description="Description",
            eligibility_criteria="Eligibility",
            application_deadline=timezone.localdate() + timedelta(days=5),
            status="approved"
        )
        self.app = Application.objects.create(
            student=self.student,
            drive=self.drive,
            status="applied"
        )

    def test_application_serializer_representation(self):
        serializer = ApplicationSerializer(instance=self.app)
        data = serializer.data
        self.assertEqual(data["student_name"], "rohan")
        self.assertEqual(data["drive_title"], "Intern")

    def test_placement_history_serializer_representation(self):
        serializer = PlacementHistorySerializer(instance=self.app)
        data = serializer.data
        self.assertEqual(data["job_title"], "Intern")
        self.assertEqual(data["status"], "applied")
