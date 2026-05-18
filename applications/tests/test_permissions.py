from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from drives.models import PlacementDrive
from applications.views import ApplicationViewSet

User = get_user_model()

class ApplicationPermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.student = User.objects.create_user(username="amit", role="student")
        
        # Setup student profile to bypass profile completion check
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

    def test_student_cgpa_eligibility(self):
        view = ApplicationViewSet.as_view({'post': 'create'})
        
        # Lower CGPA student attempts to apply
        low_cgpa_student = User.objects.create_user(username="lowcgpa", role="student")
        p = low_cgpa_student.studentprofile
        p.phone = "9876543210"
        p.branch = "Computer Science"
        p.cgpa = 7.0  # Under 8.0
        p.batch_year = 2026
        p.save()

        request = self.factory.post('/api/applications/', {"drive": self.drive.id}, format="json")
        force_authenticate(request, user=low_cgpa_student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("CGPA", str(response.data))

    def test_student_branch_eligibility(self):
        view = ApplicationViewSet.as_view({'post': 'create'})
        
        # Different branch student attempts to apply
        wrong_branch_student = User.objects.create_user(username="wrongbranch", role="student")
        p = wrong_branch_student.studentprofile
        p.phone = "9876543210"
        p.branch = "Mechanical Engineering"  # Not eligible
        p.cgpa = 9.0
        p.batch_year = 2026
        p.save()

        request = self.factory.post('/api/applications/', {"drive": self.drive.id}, format="json")
        force_authenticate(request, user=wrong_branch_student)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("branch", str(response.data))
