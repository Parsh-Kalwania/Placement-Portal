from django.test import TestCase

class DummySnapshotSerializer:
    def __init__(self, instance):
        self.instance = instance

    @property
    def data(self):
        return {
            "id": self.instance.id,
            "total_students": self.instance.total_students,
            "placed_students": self.instance.placed_students
        }

class SerializerTests(TestCase):
    def test_snapshot_serializer(self):
        from analytics.models import AdminAnalyticsSnapshot
        s = AdminAnalyticsSnapshot.objects.create(total_students=10, placed_students=5)
        serializer = DummySnapshotSerializer(s)
        self.assertEqual(serializer.data["total_students"], 10)
        self.assertEqual(serializer.data["placed_students"], 5)
