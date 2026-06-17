from .models import Notification
from django.db.models import Q

def contest_and_group_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            Q(type='group', user=request.user.profile) | 
            Q(type='contest'),
            is_active=True
        ).order_by("-created_at")[:3]
        
        return {
            "on_page_notifications" : notifications
        }
        
    return {}

def has_unread_personal_notification(request):
    if request.user.is_authenticated:
        return {
            "has_unread_personal_notifications": Notification.has_unread(type='personal', user=request.user)
        }
        
    return {}

def has_unread_group_notification(request):
    if request.user.is_authenticated:
        return {
            'has_unread_group_notifications': 
                Notification.has_unread(type='group', user=request.user) or
                Notification.has_unread(type='contest')
        }
        
    return {}