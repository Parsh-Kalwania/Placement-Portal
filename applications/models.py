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

    class Meta:
        unique_together = ('student', 'drive')

    def __str__(self):
        return f"{self.student.username} - {self.drive.job_title}"