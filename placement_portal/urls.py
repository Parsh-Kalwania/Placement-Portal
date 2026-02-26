"""
URL configuration for placement_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from drives.views import PlacementDriveViewSet
from applications.views import ApplicationViewSet

from users.views import StudentRegisterView, CompanyRegisterView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from dashboard.views import login_view, student_signup_page, company_signup_page, root_view, dashboard_page, admin_dashboard_page, company_add_drive_page
from dashboard.views import company_dashboard_page, company_complete_profile_page, company_edit_profile_page, student_dashboard_page, company_drive_detail_page
from dashboard.views import student_drive_detail_page, student_edit_profile_page, company_student_profile_page

router = DefaultRouter()
router.register(r'drives', PlacementDriveViewSet, basename='drives')
router.register(r'applications', ApplicationViewSet, basename='applications')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    path('api/register/student/', StudentRegisterView.as_view()),
    path('api/register/company/', CompanyRegisterView.as_view()),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/', include('users.urls')),
    path('api/', include('drives.urls')),
    path('api/', include('dashboard.urls')),
    
    path('', root_view),
    path('login/', login_view),
    path('signup/student/', student_signup_page),
    path('signup/company/', company_signup_page),
    
    path("company/dashboard/", company_dashboard_page),
    path("company/complete-profile/", company_complete_profile_page),
    path("company/edit-profile/", company_edit_profile_page),
    
    path("student/dashboard/", student_dashboard_page),
    
    path("admin-panel/dashboard/", admin_dashboard_page),
    
    path("company/add-drive/", company_add_drive_page),
    path("company/drive/<int:pk>/", company_drive_detail_page),
    path("student/drive/<int:pk>/", student_drive_detail_page),
    path("student/edit-profile/", student_edit_profile_page),
    path("company/student/<int:pk>/", company_student_profile_page),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)