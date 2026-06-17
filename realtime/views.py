from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from .notif_services.notif_handling import NotifHandling
from .models import Notification

class MarkNotifAsRead(View):
    def post(self, request):
        notif_id = request.POST.get('notif_id')
        try:
            NotifHandling.mark_as_read(notif_id)
        except Notification.DoesNotExist as e:
            messages.error(request, str(e))
            return JsonResponse({"success": False,},
                                status=404)
        
        return JsonResponse({"success": True})