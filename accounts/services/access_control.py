def complete_profile(user):
    if user.is_authenticated:
        return not user.profile.profile_username
    return False