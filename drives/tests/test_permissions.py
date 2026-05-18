from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from drives.views import PlacementDriveViewSet

User = get_user_model()

class DrivesPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        self.approved_company = User.objects.create_user(username="netflix", role="company", is_approved=True)
        # Setup company profile for approved company to bypass incomplete profile check
        from users.models import CompanyProfile
        profile = self.approved_company.companyprofile
        profile.company_name = "Netflix"
        profile.hr_contact = "9998887776"
        profile.save()
        
        self.unapproved_company = User.objects.create_user(username="startup", role="company", is_approved=False)
        self.student = User.objects.create_user(username="ayush", role="student")
        
        # Fully valid payload to bypass serializer field validation
        self.valid_payload = {
            "job_title": "Software Intern",
            "job_description": "We need python devs.",
            "eligibility_criteria": "CGPA > 7",
            "application_deadline": timezone.localdate() + timedelta(days=5),
            "ctc": 14.50,
            "openings": 2
        }

    def test_only_approved_company_can_create_drive(self):
        view = PlacementDriveViewSet.as_view({'post': 'create'})
        
        # Student cannot create (returns 403 Forbidden)
        request = self.factory.post('/api/drives/', self.valid_payload, format="json")
        force_authenticate(request, user=self.student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Unapproved company cannot create (returns 403 Forbidden)
        request = self.factory.post('/api/drives/', self.valid_payload, format="json")
        force_authenticate(request, user=self.unapproved_company)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
