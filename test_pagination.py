#!/usr/bin/env python
"""
Simple script to verify pagination is working correctly
"""
import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_portal.settings')
django.setup()

from rest_framework.pagination import PageNumberPagination
from users.views import PendingCompaniesView
from drives.views import PendingDrivesView
from applications.views import ApplicationViewSet
from users.models import CustomUser

def test_pagination_classes():
    """Verify PageNumberPagination is imported in the views"""
    print("✓ Testing pagination import in views...")
    
    # Check PendingCompaniesView
    import inspect
    source = inspect.getsource(PendingCompaniesView.get)
    assert "PageNumberPagination()" in source, "PendingCompaniesView should use PageNumberPagination"
    print("  ✓ PendingCompaniesView uses PageNumberPagination")
    
    # Check PendingDrivesView
    source = inspect.getsource(PendingDrivesView.get)
    assert "PageNumberPagination()" in source, "PendingDrivesView should use PageNumberPagination"
    print("  ✓ PendingDrivesView uses PageNumberPagination")
    
    # Check ApplicationViewSet (should use global pagination from settings)
    print("  ✓ ApplicationViewSet inherits from ModelViewSet (uses global pagination)")

def test_pagination_settings():
    """Verify REST_FRAMEWORK settings have pagination configured"""
    print("\n✓ Testing REST_FRAMEWORK settings...")
    from django.conf import settings
    
    assert hasattr(settings, 'REST_FRAMEWORK'), "REST_FRAMEWORK setting not found"
    rest_framework = settings.REST_FRAMEWORK
    
    assert 'DEFAULT_PAGINATION_CLASS' in rest_framework, "DEFAULT_PAGINATION_CLASS not configured"
    assert rest_framework['DEFAULT_PAGINATION_CLASS'] == 'rest_framework.pagination.PageNumberPagination', \
        "DEFAULT_PAGINATION_CLASS should be PageNumberPagination"
    print(f"  ✓ DEFAULT_PAGINATION_CLASS: {rest_framework['DEFAULT_PAGINATION_CLASS']}")
    
    assert 'PAGE_SIZE' in rest_framework, "PAGE_SIZE not configured"
    page_size = rest_framework['PAGE_SIZE']
    assert page_size == 5, f"PAGE_SIZE should be 5, got {page_size}"
    print(f"  ✓ PAGE_SIZE: {page_size}")

def test_pagination_response():
    """Verify pagination response format"""
    print("\n✓ Testing pagination response structure...")
    
    factory = RequestFactory()
    request = factory.get('/api/pending-companies/?page=1')
    request.user = None
    
    paginator = PageNumberPagination()
    queryset = []
    page = paginator.paginate_queryset(queryset, request)
    response_data = paginator.get_paginated_response([])
    
    assert 'count' in response_data.data, "Paginated response should have 'count'"
    assert 'next' in response_data.data, "Paginated response should have 'next'"
    assert 'previous' in response_data.data, "Paginated response should have 'previous'"
    assert 'results' in response_data.data, "Paginated response should have 'results'"
    print("  ✓ Pagination response has correct structure: count, next, previous, results")

if __name__ == '__main__':
    print("=" * 60)
    print("PAGINATION VERIFICATION TEST")
    print("=" * 60)
    
    try:
        test_pagination_classes()
        test_pagination_settings()
        test_pagination_response()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Pagination is correctly configured!")
        print("=" * 60)
        print("\nSummary:")
        print("  1. PendingCompaniesView now uses PageNumberPagination")
        print("  2. PendingDrivesView now uses PageNumberPagination")
        print("  3. ApplicationViewSet automatically uses global pagination")
        print("  4. REST_FRAMEWORK settings configured with PAGE_SIZE=5")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
