from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('company', 'Company'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_approved = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_companies',
        limit_choices_to={'is_superuser': True},
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    def approve(self, admin_user=None):
        self.is_approved = True
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save(update_fields=['is_approved', 'approved_by', 'approved_at'])
    
from django.conf import settings
from django.core.exceptions import ValidationError
import os

def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("Maximum file size is 5MB")

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Only PDF and DOC/DOCX are allowed.')

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/%Y/%m/', blank=True, null=True, validators=[validate_file_size, validate_file_extension])
    branch = models.CharField(max_length=100, blank=True)
    cgpa = models.FloatField(blank=True, null=True)
    batch_year = models.PositiveSmallIntegerField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    graduation_year = models.PositiveSmallIntegerField(blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # New Fields (Phase 2)
    tenth_marks = models.FloatField(blank=True, null=True, help_text="Percentage or CGPA")
    twelfth_marks = models.FloatField(blank=True, null=True, help_text="Percentage or CGPA")
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preferred_locations = models.CharField(max_length=255, blank=True)
    placement_status = models.CharField(max_length=50, default='Unplaced')
    previous_internships = models.TextField(blank=True)

    def __str__(self):
        return f"Student: {self.user.username}"

class Education(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='education_history')
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    year_of_passing = models.IntegerField()
    percentage = models.FloatField()

    def __str__(self):
        return f"{self.degree} - {self.student.user.username}"

class Project(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.ManyToManyField(Skill, blank=True)
    link = models.URLField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.username}"


class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    hr_contact = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    
    # New Fields (Phase 2)
    company_size = models.CharField(max_length=50, blank=True)
    industry_type = models.CharField(max_length=100, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    founded_year = models.PositiveSmallIntegerField(blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Company: {self.company_name}"


import uuid

class DeveloperAPIKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100, default='Default Key')
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    @staticmethod
    def generate_key_string():
        return f"pp_live_{uuid.uuid4().hex}"
