from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from users.models import DeveloperAPIKey

User = get_user_model()

class APIKeyTests(APITestCase):
    def setUp(self):
        # Create standard test student user
        self.student = User.objects.create_user(
            username="testdev",
            email="dev@example.com",
            password="123",
            role="student"
        )
        self.client.force_authenticate(user=self.student)

    def test_generate_api_key(self):
        response = self.client.post('/api/developer/keys/', {"name": "Test Key"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("key", response.data)
        self.assertEqual(response.data["name"], "Test Key")
        
        # Verify stored in database
        key_exists = DeveloperAPIKey.objects.filter(user=self.student, name="Test Key").exists()
        self.assertTrue(key_exists)

    def test_list_api_keys(self):
        # Create a key
        key_str = DeveloperAPIKey.generate_key_string()
        DeveloperAPIKey.objects.create(
            user=self.student,
            name="My List Key",
            key=key_str
        )
        
        response = self.client.get('/api/developer/keys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "My List Key")
        self.assertIn("key_preview", response.data[0])

    def test_revoke_api_key(self):
        # Create a key
        key_obj = DeveloperAPIKey.objects.create(
            user=self.student,
            name="Revoke Me",
            key=DeveloperAPIKey.generate_key_string()
        )
        
        response = self.client.delete(f'/api/developer/keys/{key_obj.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Verify deleted
        self.assertFalse(DeveloperAPIKey.objects.filter(pk=key_obj.id).exists())

    def test_authenticate_with_api_key(self):
        # Generate key
        key_str = DeveloperAPIKey.generate_key_string()
        DeveloperAPIKey.objects.create(
            user=self.student,
            name="Access Key",
            key=key_str
        )
        
        # Clear client session authentication to test API key
        self.client.logout()
        self.client.force_authenticate(user=None)
        
        # Try fetching dashboard without any authentication - should fail
        response = self.client.get('/api/student/dashboard/')
        self.assertEqual(response.status_code, 401)
        
        # Fetch with API key in header - should succeed
        self.client.credentials(HTTP_X_API_KEY=key_str)
        response = self.client.get('/api/student/dashboard/')
        self.assertEqual(response.status_code, 200)
