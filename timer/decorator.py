from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def permission_required(permission_classes):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            for p in permission_classes:
                perm = p()
                if not perm.has_permission(request):
                    if hasattr(perm, "message"):
                        messages.error(request, perm.message)
                    return redirect(p.redirect_url_name)  
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator