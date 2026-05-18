from django.test import TestCase
from users.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class SerializerTests(TestCase):
    def test_student_register_serializer_valid(self):
        data = {
            "username": "rohit",
            "email": "rohit@example.com",
            "password": "123"
        }
        serializer = RegisterSerializer(data=data, context={'role': 'student'})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.role, 'student')
        self.assertEqual(user.username, 'rohit')

    def test_company_register_serializer_valid(self):
        data = {
            "username": "amazon",
            "email": "careers@amazon.com",
            "password": "123"
        }
        serializer = RegisterSerializer(data=data, context={'role': 'company'})
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.role, 'company')
        self.assertFalse(user.is_approved)
