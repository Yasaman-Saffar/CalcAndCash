from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from accounts.services.access_control import complete_profile

class AccessControlMiddleware:
    ALLOWED_URLS = {
        'dashboard',
        'user_dashboard',
        'staff_dashboard',
        'profile',
    }
        
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        path = request.path
        resolver = resolve(path)
        
        if path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)
        
        if path.startswith("/admin/"):
            return self.get_response(request)
        
        if resolver.url_name and resolver.url_name.startswith("account_"):
            return self.get_response(request)
        
        if resolver.url_name and resolver.url_name == 'home':
            return self.get_response(request)
    
        if not request.user.is_authenticated:
            messages.error(
                request,
                "You must login or sign up first."
            )
            return redirect("home")
        
        if resolver.url_name and resolver.url_name in self.ALLOWED_URLS:
            return self.get_response(request)
        
        
        if complete_profile(request.user):
            messages.warning(
                request,
                "You must first complete your profile."
            )
            return redirect("profile")
        
        return self.get_response(request)