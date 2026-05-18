from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from dashboard.models import Notification, SupportQuery
from drives.models import PlacementDrive

User = get_user_model()

class DashboardSignalsAndModelsTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        self.student = User.objects.create_user(username="amit", role="student")

    def test_support_query_signals_notification(self):
        query = SupportQuery.objects.create(
            user=self.student,
            subject="Bug report",
            message="Resume upload fails"
        )
        # Check signal generated admin notification
        notifications = Notification.objects.filter(user=self.admin)
        self.assertTrue(notifications.exists())
        self.assertIn("Bug report", notifications.first().message)

    def test_company_registration_signals_notification(self):
        company = User.objects.create_user(username="spacex", role="company")
        # Check signal generated admin notification
        notifications = Notification.objects.filter(user=self.admin, message__contains="spacex")
        self.assertTrue(notifications.exists())

    def test_drive_post_signals_notification(self):
        company = User.objects.create_user(username="spacex", role="company", is_approved=True)
        drive = PlacementDrive.objects.create(
            company=company,
            job_title="Aerospace SDE",
            job_description="Description",
            eligibility_criteria="Eligibility",
            application_deadline=timezone.localdate() + timedelta(days=5),
            status="pending"
        )
        # Check signal generated admin notification
        notifications = Notification.objects.filter(user=self.admin, message__contains="Aerospace SDE")
        self.assertTrue(notifications.exists())
