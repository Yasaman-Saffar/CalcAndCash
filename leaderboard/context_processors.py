from .services.leaderboard_data import get_leaderboard

def leaderboard_context(request):
    not_allowed_urls = [
        "profile",
        
        # Players
        "account_signup",
        "user_dashboard",
        "user_messages",
        "add_group"
        
        # Staff
        "account_staff_signup",

    ]
    
    if request.resolver_match and request.resolver_match.view_name in not_allowed_urls:
        return {}
    
    data = get_leaderboard()
        
    return {"leaderboard": data}       