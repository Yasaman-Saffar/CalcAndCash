from django.db import models
from django.utils.timesince import timesince
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.models import Profile

class NotificationType(models.TextChoices):
    """
    Stores personal, group and contest notifications.
    """
    
    CONTEST = 'contest', 'Contest'
    GROUP = 'group', 'Group'
    PERSONAL = 'personal', 'Personal'
    
class ContextType(models.TextChoices):
    INVITATION = 'invitation', 'Invitation'
    OTP = 'otp', 'Otp'
    EVENT = 'bank-event', 'Bank-Event'

class Notification(models.Model):
    is_active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    
    type = models.CharField(max_length=10, choices=NotificationType.choices)
    context = models.CharField(max_length=15, choices=ContextType.choices)
    
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    
    header = models.TextField()
    message = models.TextField()
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.type == 'contest':
            str_shown = f'{self.type} | {self.content_object}'
        else:
            str_shown = f'{self.type} | {self.context} for {self.user}'
            
        return str_shown
    
    @classmethod
    def save_notification(cls, type, context, header, message, user=None, content_object=None):
        return cls.objects.create(
            type=type,
            context=context,
            user=user,
            header=header,
            message=message,
            content_object=content_object,
        )
        
    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])
        
    @staticmethod
    def has_unread(type, user=None):
        queryset = Notification.objects.filter(
                type=type,
                is_active=True,
                is_read=False
            )
        
        if user:
            queryset = queryset.filter(user=user.profile)
        return queryset.exists()
    
    def to_dict(self):
        passed_time = f'{timesince(self.created_at)} ago' if timesince(self.created_at) != "0 minutes" else "Just now"
        return {
            "notif_id": self.id,
            "type": self.type,
            "context": self.context,
            "header": self.header,
            "message": self.message,
            "time": passed_time,
        }
        