from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsCompany(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'company'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'student'
    
class IsNotBlacklisted(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_blacklisted:
            raise PermissionDenied("Your account has been blacklisted. Please contact admin.")
        return True