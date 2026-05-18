from django.urls import path
from .views import (
    ApproveCompanyView, CompanyProfileView, MeView, PendingCompaniesView,
    StudentDashboardView, CompanyDashboardView, StudentProfileView,
    CompanyViewStudentProfile, DeveloperAPIKeyView
)

urlpatterns = [
    path('admin/companies/pending/', PendingCompaniesView.as_view()),
    path('admin/companies/<int:pk>/approve/', ApproveCompanyView.as_view()),
    path("company/profile/", CompanyProfileView.as_view()),
    path("me/", MeView.as_view()),
    path("student/dashboard/", StudentDashboardView.as_view()),
    path("company/dashboard/", CompanyDashboardView.as_view()),
    path("student/profile/", StudentProfileView.as_view()),
    path("company/student/<int:pk>/", CompanyViewStudentProfile.as_view()),
    path("developer/keys/", DeveloperAPIKeyView.as_view()),
    path("developer/keys/<int:pk>/", DeveloperAPIKeyView.as_view()),
]
