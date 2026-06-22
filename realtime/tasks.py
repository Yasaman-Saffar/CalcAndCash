from celery import shared_task
from .models import Notification
from .services import notify, notify_all_players

@shared_task
def send_notification_task(user_id, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return
    
    notify(user_id, notification.to_dict())
    
# @shared_task
# def send_all_notification_task(notification_id):
#     notification = Notification.objects.get(id=notification_id)
#     notify_all_players(notification.to_dict())