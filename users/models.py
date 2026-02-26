from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('company', 'Company'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_approved = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
from django.conf import settings

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    resume = models.URLField(blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True)
    cgpa = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Student: {self.user.username}"


class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    hr_contact = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Company: {self.company_name}"