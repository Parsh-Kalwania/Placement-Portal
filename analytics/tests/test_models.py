from django.test import TestCase
from analytics.models import AdminAnalyticsSnapshot

class AdminAnalyticsSnapshotModelTest(TestCase):
    def test_create_snapshot(self):
        snapshot = AdminAnalyticsSnapshot.objects.create(
            total_students=100,
            placed_students=60,
            total_companies=10,
            total_drives=20,
            avg_salary=12.50,
            branch_stats={"CSE": 40, "ECE": 20},
            company_stats={"Netflix": 15}
        )
        self.assertEqual(snapshot.total_students, 100)
        self.assertEqual(float(snapshot.avg_salary), 12.50)
        self.assertIn("Snapshot -", str(snapshot))
