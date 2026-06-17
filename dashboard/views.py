from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, ListView
from Core.permissions import IsPlayer, IsStaff
from Core.mixins import PermissionRequiredMixin

from realtime.models import Notification
from accounts.models import Profile
from groups.models import ContestGroup
from timer.models import TimeControl
from bank.models import Event


class DashboardRedirectView(View):
    def get(self, request):
        user = request.user
        if user.is_staff:
            return redirect('staff_dashboard')
            
        else:
            return redirect('user_dashboard')
            
class UserDashboardView(PermissionRequiredMixin, TemplateView):
    permission_classes = [IsPlayer]
    template_name = 'dashboard/user_dashboard.html'
    
    def get(self, request):
        user_group = request.user.profile.group
        return render(request, self.template_name, {'user_group': user_group})
        
    
class StaffDashboardView(PermissionRequiredMixin, TemplateView):
    permission_classes = [IsStaff]
    template_name = 'dashboard/staff_dashboard.html'

    
    def get(self, request,):
        total_groups = ContestGroup.objects.all().count()
        total_users = Profile.objects.filter(user__is_staff=False).count()
        contest_duration = TimeControl.objects.first().duration if TimeControl.objects.first() else None
        total_inflations = Event.objects.filter(type="inflation").count()
        total_interests = Event.objects.filter(type="interest").count()
        
        return render(request ,self.template_name, {"total_groups": total_groups,
                                                    "total_users": total_users,
                                                    "contest_duration": contest_duration,
                                                    "total_inflations": total_inflations,
                                                    "total_interests": total_interests,})
    
class UserMessages(ListView):
    model = Notification
    context_object_name = 'notifications'
    template_name = 'dashboard/user_notifications.html'
    paginate_by = 7
    
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(type='personal', user=self.request.user.profile, is_active=True)
            .order_by("-created_at")
        )
    