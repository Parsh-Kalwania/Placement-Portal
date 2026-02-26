from django.contrib import admin
from .models import PlacementDrive


@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'status', 'application_deadline', 'created_at')
    list_filter = ('status', 'application_deadline')
    search_fields = ('job_title', 'company__username')