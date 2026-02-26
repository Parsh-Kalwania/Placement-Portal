from django.db import models
from django.conf import settings

class PlacementDrive(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
    )

    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'company'}
    )

    job_title = models.CharField(max_length=200)
    job_description = models.TextField()
    eligibility_criteria = models.TextField()
    application_deadline = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} - {self.company.username}"