from django.urls import path
from .views import ApproveCompanyView, CompanyProfileView, MeView, StudentDashboardView, CompanyDashboardView, StudentProfileView,CompanyViewStudentProfile

urlpatterns = [
    path('admin/companies/<int:pk>/approve/', ApproveCompanyView.as_view()),
    path("company/profile/", CompanyProfileView.as_view()),
    path("me/", MeView.as_view()),
    path("student/dashboard/", StudentDashboardView.as_view()),
    path("company/dashboard/", CompanyDashboardView.as_view()),
    path("student/profile/", StudentProfileView.as_view()),
    path("company/student/<int:pk>/", CompanyViewStudentProfile.as_view()),
]