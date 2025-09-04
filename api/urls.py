"""
URL configuration for api app.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # API endpoints will be added here
    # Example:
    # path('users/', views.UserListView.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
] 