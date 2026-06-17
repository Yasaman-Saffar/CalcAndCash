from django.urls import path
from . import views

urlpatterns = [
    path('mark-notif-asRead/', views.MarkNotifAsRead.as_view(), name='mark-as-read'),
]