from django.urls import path
from .views import AdminDashboardStatsView
from .views import PlacementHistoryView
from .views import CompanyDashboardView

urlpatterns = [
    path('admin/dashboard/', AdminDashboardStatsView.as_view()),
    path('student/placement-history/', PlacementHistoryView.as_view()),
    path('company/dashboard/', CompanyDashboardView.as_view()),
]