from django.contrib import admin
from .models import ContestGroup, GroupMembership, GroupInvitation

@admin.register(ContestGroup)
class ContestGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('group__name', 'invitee', 'invitor', 'invitation_status')
    search_fields = ('group__name', 'invitee', 'invitor')
    list_filter = ('invitation_status',)

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('group__name', 'member__profile_username', 'is_leader', 'joined_at')
    search_fields = ('group__name', 'member__profile_username')
    list_filter = ('group', 'is_leader')