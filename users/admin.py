from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, CompanyProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_blacklisted', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_blacklisted', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Status', {
            'fields': ('role', 'is_approved', 'is_blacklisted'),
        }),
    )


admin.site.register(StudentProfile)
admin.site.register(CompanyProfile)