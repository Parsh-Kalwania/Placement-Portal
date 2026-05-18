from django.db import models
from django.conf import settings
from django.utils import timezone

class PlacementDrive(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
    )

    JOB_TYPE_CHOICES = (
        ('fulltime', 'Full-time'),
        ('internship', 'Internship'),
        ('parttime', 'Part-time'),
        ('contract', 'Contract'),
    )

    WORK_MODES = (
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('onsite', 'On-site'),
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
    ctc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES, default='fulltime')
    work_mode = models.CharField(max_length=20, choices=WORK_MODES, default='onsite')
    required_skills = models.ManyToManyField('users.Skill', blank=True)
    openings = models.PositiveIntegerField(default=1)
    
    # New Fields (Phase 2)
    min_cgpa = models.FloatField(default=0.0)
    eligible_branches = models.JSONField(default=list, blank=True)
    selection_stages = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} - {self.company.username}"

    @classmethod
    def close_expired(cls):
        return cls.objects.filter(
            status='approved',
            application_deadline__lt=timezone.localdate(),
        ).update(status='closed')
