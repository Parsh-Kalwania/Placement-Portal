from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class UserViewsTestCase(APITestCase):
    def setUp(self):
        self.student_data = {
            "username": "rohan",
            "email": "rohan@example.com",
            "password": "123"
        }
        self.company_data = {
            "username": "netflix",
            "email": "jobs@netflix.com",
            "password": "123"
        }
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")

    def test_student_registration(self):
        response = self.client.post("/api/register/student/", self.student_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="rohan", role="student").exists())

    def test_company_registration(self):
        response = self.client.post("/api/register/company/", self.company_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="netflix")
        self.assertEqual(user.role, "company")
        self.assertFalse(user.is_approved)

    def test_jwt_auth_flow(self):
        # Register student
        self.client.post("/api/register/student/", self.student_data, format="json")
        
        # Get Token
        response = self.client.post("/api/token/", {
            "username": "rohan",
            "password": "123"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        
        access_token = response.data["access"]
        
        # Access authenticated me view
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_response = self.client.get("/api/me/")
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["role"], "student")

    def test_approve_company_view(self):
        company = User.objects.create_user(username="netflix", role="company")
        self.assertFalse(company.is_approved)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f"/api/admin/companies/{company.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company.refresh_from_db()
        self.assertTrue(company.is_approved)

    def test_student_profile_update_and_file_upload(self):
        student = User.objects.create_user(username="rohan", role="student")
        self.client.force_authenticate(user=student)
        
        # Mock resume file
        resume_file = SimpleUploadedFile("resume.pdf", b"pdf content here", content_type="application/pdf")
        
        data = {
            "phone": "+919876543210",
            "branch": "Computer Science",
            "cgpa": "8.5",
            "batch_year": 2026,
            "resume": resume_file,
            "linkedin_url": "https://linkedin.com/in/rohan",
            "github_url": "https://github.com/rohan"
        }
        
        response = self.client.patch("/api/student/profile/", data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        student.studentprofile.refresh_from_db()
        self.assertEqual(student.studentprofile.phone, "+919876543210")
        self.assertEqual(float(student.studentprofile.cgpa), 8.5)
        self.assertTrue(bool(student.studentprofile.resume))
