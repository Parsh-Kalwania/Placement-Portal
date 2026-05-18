from drives.views import ApproveDriveView, CompanyDriveDetailView, PendingDrivesView, StudentDriveDetailView
from django.urls import path

urlpatterns = [
    path('admin/drives/pending/', PendingDrivesView.as_view()),
    path('admin/drives/<int:pk>/approve/', ApproveDriveView.as_view()),
    path("company/drive/<int:pk>/", CompanyDriveDetailView.as_view()),
    path("student/drive/<int:pk>/", StudentDriveDetailView.as_view()),
]
