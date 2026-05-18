from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from drives.serializers import PlacementDriveSerializer

User = get_user_model()

class PlacementDriveSerializerTest(TestCase):
    def setUp(self):
        self.company = User.objects.create_user(
            username="netflix",
            role="company",
            is_approved=True
        )

    def test_serializer_validation_errors(self):
        # Test past deadline
        past_deadline = timezone.localdate() - timedelta(days=1)
        data = {
            "job_title": "Software Engineer",
            "job_description": "Cool role",
            "eligibility_criteria": "Must love code",
            "application_deadline": past_deadline,
            "ctc": 12.0,
            "openings": 5
        }
        serializer = PlacementDriveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("application_deadline", serializer.errors)

        # Test negative CTC
        data["application_deadline"] = timezone.localdate() + timedelta(days=5)
        data["ctc"] = -2.0
        serializer = PlacementDriveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("ctc", serializer.errors)

        # Test invalid openings
        data["ctc"] = 12.0
        data["openings"] = 0
        serializer = PlacementDriveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("openings", serializer.errors)

    def test_serializer_success_and_skills_save(self):
        deadline = timezone.localdate() + timedelta(days=5)
        data = {
            "job_title": "Fullstack Engineer",
            "job_description": "Cool role",
            "eligibility_criteria": "Must love code",
            "application_deadline": deadline,
            "ctc": 12.0,
            "openings": 5,
            "required_skills": "Python, Django, React"
        }
        serializer = PlacementDriveSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Save drive (needs company from perform_create in view, so we pass it manually to save)
        drive = serializer.save(company=self.company)
        self.assertEqual(drive.job_title, "Fullstack Engineer")
        self.assertEqual(drive.required_skills.count(), 3)
        skills = list(drive.required_skills.values_list('name', flat=True))
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
