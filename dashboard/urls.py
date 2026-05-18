from django.urls import path
from .views import AdminDashboardStatsView, AdminListModelView
from .views import PlacementHistoryView
from .views import CompanyDashboardView
from .views import NotificationListView, SupportQueryView, AdminSupportQueryView, UserSupportQueryView

urlpatterns = [
    path('admin/dashboard/', AdminDashboardStatsView.as_view()),
    path('admin/list-data/', AdminListModelView.as_view()),
    path('student/placement-history/', PlacementHistoryView.as_view()),
    path('company/dashboard/stats/', CompanyDashboardView.as_view()),
    path('notifications/', NotificationListView.as_view()),
    path('support/', SupportQueryView.as_view()),
    path('support/history/', UserSupportQueryView.as_view()),
    path('admin/support/', AdminSupportQueryView.as_view()),
    path('admin/support/<int:pk>/resolve/', AdminSupportQueryView.as_view()),
]
