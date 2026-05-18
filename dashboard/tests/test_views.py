from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from dashboard.models import Notification, SupportQuery

User = get_user_model()

class DashboardViewsTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="adminuser", email="admin@example.com", password="123")
        self.student = User.objects.create_user(username="arun", role="student")
        
        # Create some notifications
        self.notif = Notification.objects.create(user=self.student, message="Welcome to portal!")

    def test_notifications_list_and_read(self):
        self.client.force_authenticate(user=self.student)
        
        # Fetch list
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["notifications"][0]["message"], "Welcome to portal!")
        
        # Mark all as read
        read_response = self.client.post("/api/notifications/")
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        
        # Verify read count is 0
        response_after = self.client.get("/api/notifications/")
        self.assertEqual(response_after.data["count"], 0)

    def test_support_ticket_creation_and_resolution(self):
        self.client.force_authenticate(user=self.student)
        
        # Post ticket
        response = self.client.post("/api/support/", {
            "subject": "Missing course details",
            "message": "I cannot fill Twelfth standard math score."
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        ticket = SupportQuery.objects.get(subject="Missing course details")
        self.assertEqual(ticket.user, self.student)
        self.assertFalse(ticket.is_resolved)
        
        # Resolve ticket as admin
        self.client.force_authenticate(user=self.admin)
        resolve_response = self.client.patch(f"/api/admin/support/{ticket.id}/resolve/", {
            "reply": "Added the math score field, please check."
        }, format="json")
        self.assertEqual(resolve_response.status_code, status.HTTP_200_OK)
        
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_resolved)
        self.assertEqual(ticket.admin_reply, "Added the math score field, please check.")
