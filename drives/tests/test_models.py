from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive

User = get_user_model()

class PlacementDriveModelTest(TestCase):
    def setUp(self):
        self.company = User.objects.create_user(
            username="apple",
            role="company",
            is_approved=True
        )

    def test_create_drive(self):
        deadline = timezone.localdate() + timedelta(days=7)
        drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="Software Engineer Intern",
            job_description="Cool job",
            eligibility_criteria="Must know Python",
            application_deadline=deadline,
            ctc=15.00,
            status="pending"
        )
        self.assertEqual(str(drive), "Software Engineer Intern - apple")
        self.assertEqual(drive.status, "pending")
        self.assertEqual(float(drive.ctc), 15.00)

    def test_close_expired_drives(self):
        # Create an approved drive with a past deadline
        past_deadline = timezone.localdate() - timedelta(days=2)
        drive = PlacementDrive.objects.create(
            company=self.company,
            job_title="Expired Dev",
            job_description="Old job",
            eligibility_criteria="None",
            application_deadline=past_deadline,
            status="approved"
        )
        self.assertEqual(drive.status, "approved")
        
        # Call the close_expired classmethod
        PlacementDrive.close_expired()
        
        drive.refresh_from_db()
        self.assertEqual(drive.status, "closed")
