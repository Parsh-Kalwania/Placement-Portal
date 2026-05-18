from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import StudentProfile, CompanyProfile

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_student_user(self):
        user = User.objects.create_user(
            username="aravind",
            email="aravind@example.com",
            password="123",
            role="student"
        )
        self.assertEqual(user.username, "aravind")
        self.assertEqual(user.role, "student")
        self.assertFalse(user.is_approved)  # defaults to False
        
        # Test signal creates StudentProfile
        profileExists = StudentProfile.objects.filter(user=user).exists()
        self.assertTrue(profileExists)

    def test_create_company_user(self):
        user = User.objects.create_user(
            username="microsoft",
            email="recruiter@microsoft.com",
            password="123",
            role="company"
        )
        self.assertEqual(user.username, "microsoft")
        self.assertEqual(user.role, "company")
        
        # Test signal creates CompanyProfile
        profileExists = CompanyProfile.objects.filter(user=user).exists()
        self.assertTrue(profileExists)

    def test_approve_company(self):
        admin = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="123"
        )
        company = User.objects.create_user(
            username="google",
            role="company"
        )
        self.assertFalse(company.is_approved)
        company.approve(admin)
        self.assertTrue(company.is_approved)
