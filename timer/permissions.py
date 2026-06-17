class HasAccessToTimer:
    message = "You don't have access to this part."
    redirect_url_name = 'dashboard'
    
    def has_permission(self, request):
        return request.user.is_superuser