from django.db import models
from accounts.models import Profile

class ContestGroup(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def all_members(self):
        """ returns all members as queryset """
        return Profile.objects.filter(memberships__group=self)
    
    @property
    def members(self):
        """ returns all members as queryset """
        return Profile.objects.filter(memberships__group=self, memberships__is_leader=False)
    
    @property
    def leaders(self):
        """ returns all leaders as queryset """
        return Profile.objects.filter(memberships__group=self, memberships__is_leader=True)
    
    def invite_user(self, invitor, invitee):
        """ utility function to simplify member addition """
        return GroupInvitation.objects.create(
            group=self,
            invitor=invitor,
            invitee=invitee
        )
    
    def add_member(self, profile, is_leader=False):
        """ utility function to simplify member addition """
        return GroupMembership.objects.create(
            group=self,
            member=profile,
            is_leader=is_leader
        )

class GroupMembership(models.Model):
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE, related_name='memberships')
    member = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='memberships')
    is_leader = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.member.user
        return f'{user.profile.profile_username if user.profile.profile_username else user.phone} in {self.group.name}'
    
class InvitationStatus(models.TextChoices):
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    PENDING = "pending", "Pending"
    
class GroupInvitation(models.Model):
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    invitor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="invitor")
    invitee = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="invitee")
    created_at = models.DateTimeField(auto_now_add=True)
    invitation_status = models.CharField(max_length=10, choices=InvitationStatus.choices, default=InvitationStatus.PENDING)
    group_membership = models.OneToOneField(GroupMembership, on_delete=models.SET_NULL, null=True) # if a user is no longer a member, it will be set to null
    
    def __str__(self):
        return f'{self.invitation_status}: {self.invitor} invited {self.invitee} to {self.group}'
    
from django.conf import settings
from django.db import models

class GroupActions(models.TextChoices):
    ADD_GROUP = "add_group", "Add group"
    DELETE_GROUP = "delete_group", "Delete group"
    CHANGE_SETTING = "change_setting", "Change setting"
    INVITE_MEMBER = "invite_member", "Invite member"
    INVITATION_ACCEPTED = "invitation_accepted", "Invitation Accepted"
    INVITATION_REJECTED = "invitation_rejected", "Invitation Rejected"
    REMOVE_MEMBER = "remove_member", "Remove member"
    PROMOTE_MEMBER = "promote_member", "Promote member"
    BUY_QUESTION = "buy_question", "Buy question"
    SOLVE_QUESTION = "solve_question", "Solve question"
    TRADE_QUESTION_SELL = "trade_question_sell", "Trade question-Sold"
    TRADE_QUESTION_BUYER = "trade_question_buy", "Trade question-Bought"
    BUY_ITEM = "buy_item", "Buy item"
    SELL_ITEM = "sell_item", "Sell item"

class GroupActivity(models.Model):
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=50, choices=GroupActions.choices)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group} | {self.action}"
