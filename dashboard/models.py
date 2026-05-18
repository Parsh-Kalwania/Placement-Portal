from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class SupportQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_queries')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_save, sender=SupportQuery)
def notify_admin_on_support_query(sender, instance, created, **kwargs):
    if created:
        User = get_user_model()
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"• New Support Query: '{instance.subject}' submitted by {instance.user.username}."
            )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def notify_admin_on_company_registration(sender, instance, created, **kwargs):
    if created and instance.role == 'company' and not instance.is_approved:
        User = get_user_model()
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"• Pending Approval: New company '{instance.username}' registered."
            )

@receiver(post_save, sender='drives.PlacementDrive')
def notify_admin_on_drive_post(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        User = get_user_model()
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"• Pending Approval: Drive '{instance.job_title}' submitted by {instance.company.username}."
            )
