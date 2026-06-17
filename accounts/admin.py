from django.contrib import admin
from .models import CustomUser, Profile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'is_staff', 'phone_verified')
    search_fields = ('phone', 'email')
    list_filter = ('is_staff', 'phone_verified')

@admin.register(Profile)
class CustomProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_select_related = ('user',)
    list_display = ('profile_username', 'first_name', 'last_name','user__phone', 'is_player')
    list_filter = ('user__is_staff',)
    search_fields = ('user__phone', 'profile_username', 'first_name', 'last_name')
    
    @admin.display(boolean=True, description="Player")
    def is_player(self, obj):
        return not obj.user.is_staff