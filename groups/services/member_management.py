from django.shortcuts import get_object_or_404

from groups.models import GroupInvitation, GroupMembership
from accounts.models import Profile
from .exceptions import HasGroup, HasInvited
from realtime.models import Notification
from realtime.notif_services.notif_handling import NotifHandling

class MemberManagement:
    """
    Handles group invitations, membership changes and leader assignment.
    """

    @staticmethod
    def search_user(q, leader):
        group = leader.profile.group
        profiles = Profile.objects.filter(
            profile_username__icontains=q,
            user__is_staff=False
            ).exclude(
                user=leader
            )[:10]

        results = [
            {
                'id': p.id,
                'username': p.profile_username,
                'has_group': True if getattr(p, 'group') else False,
                'has_invited': MemberManagement.has_invited(group, p)
            }
            for p in profiles
        ]
        return results
    
    @staticmethod
    def has_invited(group, invitee):
        return GroupInvitation.objects.filter(
            group=group,
            invitee=invitee,
            invitation_status='pending'
        ).exists()
    
    @staticmethod
    def invite(invitee, invitor):
        """
        Send a group invitation and notify the invited user.
        """
        group = invitor.group
        if MemberManagement.has_invited(group, invitee):
            raise HasInvited(f"{invitee} has already invited by your group.")
        if invitee.group:
            raise HasGroup(f"{invitee.profile_username} already has a group: {invitee.group}")
        
        invitation = group.invite_user(invitor, invitee)
        header = "Group Invitation"
        message = f'"{invitation.invitor}" invites you to join "{invitation.group}" and team up to compete with others.'
        NotifHandling.notify_message(type='personal', context='invitation', users=[invitee], header=header, message=message, content_object=invitation) 
           
    @staticmethod
    def change_invitation_status(notification_id, status):
        notif = get_object_or_404(Notification, id=notification_id)
        invitation = notif.content_object
        invitation.invitation_status = status
        invitation.save(update_fields=['invitation_status'])
        return invitation, notif
    
    @staticmethod
    def invitation_rejection(notification_id):
        """ 
        Reject a group invitation and notify the inviter's group.
        """
        invitation, notif = MemberManagement.change_invitation_status(notification_id, "rejected")
        notif.deactivate()
        
        invitor_group_members = invitation.group.members
        invitor_group_leaders = invitation.group.leaders
        
        header = "Group Invitation"
        message = f'"{invitation.invitee}" rejected to be a part of your group.'
        all_members = list(invitor_group_leaders) + list(invitor_group_members)
        NotifHandling.notify_message(type='group', context='invitation', users=all_members, header=header, message=message, content_object=invitation)
        
    
    @staticmethod
    def invitation_acceptance(notification_id):
        """
        Accept a group invitation, add the user as a member and notify the group.
        """
        invitation, notif = MemberManagement.change_invitation_status(notification_id, "accepted")
        notif.deactivate()

        group_members = invitation.group.members
        group_leaders = invitation.group.leaders
        
        header = "Group Invitation"
        message = f'"{invitation.invitee}" is a member of your group now!'
        all_members = list(group_leaders) + list(group_members)
        NotifHandling.notify_message(type='group', context='invitation', users=all_members, header=header, message=message, content_object=invitation)
        
        gm = MemberManagement.add_member(invitation)
        invitation.group_membership = gm
        invitation.save(update_fields=['group_membership'])
    
    @staticmethod
    def add_member(invitation):
        group = invitation.group
        invitee = invitation.invitee
        gm = group.add_member(invitee)
        return gm
    
    @staticmethod
    def delete_member(selected_members_ids):
        deleted_list = []
        for id in selected_members_ids:
            gm = get_object_or_404(GroupMembership, id=id)
            gi = get_object_or_404(GroupInvitation, group_membership=gm)
            gm.delete()
            gi.group_membership = None
            gi.save()
            deleted_list.append(gm.member.profile_username)
            
        removed_members = ", ".join([str(p) for p in deleted_list])
        return removed_members
            
    @staticmethod        
    def assign_member_to_leader(selected_members_ids):
        promoted_list = []
        for id in selected_members_ids:
            gm = get_object_or_404(GroupMembership, id=id)
            gm.is_leader = True
            gm.save()
            promoted_list.append(gm.member.profile_username)
        
        promoted_members = ", ".join([str(p) for p in promoted_list])
        return promoted_members  