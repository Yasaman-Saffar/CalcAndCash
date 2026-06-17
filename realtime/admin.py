from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    list_display = ('type', 'context', 'user', 'is_read', 'is_active')
    search_fields = ('user', 'context', 'type', 'header')
    list_filter = ('context', 'type', 'is_read', 'is_active')