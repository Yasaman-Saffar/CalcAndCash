class CheckContestState:
    message = ""
    redirect_url_name = 'group-dashboard'
    
    def has_permission(self, request):
        from timer.models import TimeControl
        
        timer = TimeControl.objects.first()
        
        if timer is None:
            return request.user.is_authenticated
        
        state = timer.status
        
        if state == "not-started":
            self.message = "Contest hasn't started yet."
        elif state == "finished":
            self.message = "Time is over!"
        elif state == "paused":
            self.message = "Contest is paused."
            
        return request.user.is_staff or state == "running"
    
class IsStaff:
    message = "You don't have access to this page."
    redirect_url_name = 'dashboard'
    
    def has_permission(self, request):
        user = request.user
        return user.is_staff or user.is_superuser
    
class IsPlayer:
    message = "Staff users cannot play."
    redirect_url_name = 'dashboard'
    
    def has_permission(self, request):
        user = request.user
        return not (user.is_staff or user.is_superuser)
    
class HasGroup:
    message = "You need to join a group to have access to this page."
    redirect_url_name = 'dashboard'
    
    def has_permission(self, request):
        return request.user.profile.group
    
class IsGroupLeader:
    message = "You don't have access to this page."
    redirect_url_name = 'group-dashboard'
    
    def has_permission(self, request):
        return request.user.profile.memberships.is_leader