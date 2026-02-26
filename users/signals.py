from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudentProfile, CompanyProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, **kwargs):

    if instance.role == 'student':
        if not hasattr(instance, 'studentprofile'):
            StudentProfile.objects.create(user=instance)

    elif instance.role == 'company':
        if not hasattr(instance, 'companyprofile'):
            CompanyProfile.objects.create(user=instance)