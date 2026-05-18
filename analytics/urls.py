from django.urls import path
from .views import (
    StudentAnalyticsView,
    CompanyAnalyticsView,
    AdminAnalyticsView,
    SmartMatchView,
)

urlpatterns = [
    path('student/analytics/', StudentAnalyticsView.as_view()),
    path('company/analytics/', CompanyAnalyticsView.as_view()),
    path('admin/analytics/', AdminAnalyticsView.as_view()),
    path('student/smart-matches/', SmartMatchView.as_view()),
]
