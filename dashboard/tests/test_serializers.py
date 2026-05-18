from django.test import TestCase
from dashboard.models import Notification

class DummyNotificationSerializer:
    def __init__(self, instance):
        self.instance = instance

    @property
    def data(self):
        return {
            "id": self.instance.id,
            "message": self.instance.message,
            "is_read": self.instance.is_read
        }

class SerializerTests(TestCase):
    def test_notification_representation(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username="amit")
        n = Notification.objects.create(user=user, message="Hello Notification")
        
        serializer = DummyNotificationSerializer(n)
        self.assertEqual(serializer.data["message"], "Hello Notification")
        self.assertFalse(serializer.data["is_read"])
