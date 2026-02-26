from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'drive', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'drive__job_title')