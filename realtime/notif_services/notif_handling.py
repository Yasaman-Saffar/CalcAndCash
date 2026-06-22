from django.shortcuts import get_object_or_404
from ..tasks import send_notification_task, send_all_notification_task
from ..models import Notification

class NotifHandling:
    """
    Creates notifications and dispatches websocket delivery tasks.
    """
    
    @staticmethod
    def notify_message(type, context, users, header, message, content_object=None):  
        for user in users:
            notification = Notification.save_notification(
                type=type, 
                context=context,
                user=user, 
                header=header, 
                message=message,
                content_object=content_object)
            
            send_notification_task.delay(user.id, notification.id)  
    
    @staticmethod
    def mark_as_read(id):
        notif = get_object_or_404(Notification, id=id)
        notif.is_read = True
        notif.save(update_fields=['is_read'])