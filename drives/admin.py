from django.contrib import admin
from .models import PlacementDrive


@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'job_type', 'ctc', 'location', 'openings', 'status', 'application_deadline', 'created_at')
    list_filter = ('status', 'job_type', 'application_deadline')
    search_fields = ('job_title', 'company__username', 'location', 'required_skills')
