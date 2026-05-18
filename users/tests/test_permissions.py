from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from users.permissions import IsAdminUserRole, IsCompany, IsStudent, IsNotBlacklisted
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.student = User.objects.create_user(username="amit", role="student")
        self.company = User.objects.create_user(username="netflix", role="company")
        self.admin = User.objects.create_superuser(username="root", email="root@example.com")
        self.blacklisted_student = User.objects.create_user(username="spam", role="student", is_blacklisted=True)

    def test_is_admin_user_role(self):
        perm = IsAdminUserRole()
        request = self.factory.get('/')
        
        request.user = self.admin
        self.assertTrue(perm.has_permission(request, None))
        
        request.user = self.student
        self.assertFalse(perm.has_permission(request, None))

    def test_is_company(self):
        perm = IsCompany()
        request = self.factory.get('/')
        
        request.user = self.company
        self.assertTrue(perm.has_permission(request, None))
        
        request.user = self.student
        self.assertFalse(perm.has_permission(request, None))

    def test_is_student(self):
        perm = IsStudent()
        request = self.factory.get('/')
        
        request.user = self.student
        self.assertTrue(perm.has_permission(request, None))
        
        request.user = self.company
        self.assertFalse(perm.has_permission(request, None))

    def test_is_not_blacklisted(self):
        perm = IsNotBlacklisted()
        request = self.factory.get('/')
        
        request.user = self.student
        self.assertTrue(perm.has_permission(request, None))
        
        request.user = self.blacklisted_student
        with self.assertRaises(PermissionDenied):
            perm.has_permission(request, None)
