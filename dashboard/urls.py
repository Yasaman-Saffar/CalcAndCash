from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardRedirectView.as_view(), name='dashboard'),
    path('user/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('messages/', views.UserMessages.as_view(), name='user_messages' ),
    path('staff/', views.StaffDashboardView.as_view(), name='staff_dashboard'),
]
