from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import DeveloperAPIKey
from django.utils import timezone

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key_str = request.headers.get('X-API-Key') or request.query_params.get('api_key')
        if not api_key_str:
            return None  # Fallback to standard session/JWT authentication
            
        try:
            key_obj = DeveloperAPIKey.objects.select_related('user').get(key=api_key_str, is_active=True)
        except DeveloperAPIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive Developer API Key.")
            
        # Update last used timestamp
        key_obj.last_used = timezone.now()
        key_obj.save(update_fields=['last_used'])
        
        # DRF expects a tuple of (user, auth)
        return (key_obj.user, key_obj)
