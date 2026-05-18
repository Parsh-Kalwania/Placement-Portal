from django.db import models

class AdminAnalyticsSnapshot(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    total_students = models.IntegerField(default=0)
    placed_students = models.IntegerField(default=0)
    total_companies = models.IntegerField(default=0)
    total_drives = models.IntegerField(default=0)
    avg_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    branch_stats = models.JSONField(default=dict)
    company_stats = models.JSONField(default=dict)

    def __str__(self):
        return f"Snapshot - {self.timestamp.date()}"
