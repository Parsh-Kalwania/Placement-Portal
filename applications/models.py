from django.db import models
from django.conf import settings
from drives.models import PlacementDrive


class Application(models.Model):

    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    drive = models.ForeignKey(
        PlacementDrive,
        on_delete=models.CASCADE
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    current_round = models.CharField(max_length=100, blank=True)
    company_notes = models.TextField(blank=True)
    
    # Phase 2 Fields
    cover_letter = models.TextField(blank=True)
    current_stage = models.CharField(max_length=100, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    company_feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'drive')

    def __str__(self):
        return f"{self.student.username} - {self.drive.job_title}"

class ApplicationTimeline(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline')
    stage = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.application} - {self.stage}"
