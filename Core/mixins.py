from django.contrib import messages
from django.shortcuts import redirect

class PermissionRequiredMixin:
    """
    Checks custom permission classes before dispatching the request.
    """
    
    permission_classes = []
    
    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            p = permission()
            if not p.has_permission(request):
                messages.error(request, p.message)
                return redirect(p.redirect_url_name)
        return super().dispatch(request, *args, **kwargs)