from drives.views import ApproveDriveView, CompanyDriveDetailView, StudentDriveDetailView
from django.urls import path

urlpatterns = [
    path('api/admin/drives/<int:pk>/approve/', ApproveDriveView.as_view()),
    path("company/drive/<int:pk>/", CompanyDriveDetailView.as_view()),
    path("student/drive/<int:pk>/", StudentDriveDetailView.as_view()),
]