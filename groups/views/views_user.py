from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import CreateView, View, UpdateView, DeleteView, TemplateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ..models import ContestGroup, GroupMembership, GroupInvitation, GroupActivity
from ..services.member_management import MemberManagement
from ..services.group_question_handling import QuestionHandling
from ..services.exceptions import GroupErrors, GroupQuestionErrors
from ..services.group_logs import log_group_activity
from bank.models import BankAccount, GroupQuestion
from bank.services.transaction_processor import TransactionProcessor 
from accounts.models import Profile
from realtime.models import Notification
from Core.mixins import PermissionRequiredMixin
from Core.permissions import HasGroup, IsGroupLeader, CheckContestState, IsPlayer


#========================================================= GROUP MANAGEMENT =========================================================
class AddGroup(PermissionRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Creates a new group and assigns the creator as its first leader.
    """
    permission_classes = [IsPlayer]
    model = ContestGroup
    fields = ['name']
    template_name = 'groups/user/create.html'
    context_object_name = 'form'
    success_url = reverse_lazy('group-dashboard')
    
    def test_func(self):
        return not self.request.user.profile.group
        
    def handle_no_permission(self):
        messages.error(self.request, "You already have a group!")
        return redirect("group-dashboard") 
    
    def form_valid(self, form):
        response = super().form_valid(form)
        leader_profile = self.request.user.profile
        
        self.object.add_member(leader_profile, is_leader=True)
        BankAccount.new_bank_account(self.object)

        messages.success(self.request, f'The group "{self.object.name}" was created successfully.')
        log_group_activity(
            group=self.object,
            action="add_group",
            message=f'{self.request.user.profile.profile_username} created "{self.object.name}".'
        )
        return response

class DeleteGroup(PermissionRequiredMixin, DeleteView):
    permission_classes = [IsPlayer ,HasGroup, IsGroupLeader]
    model = ContestGroup
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user.profile.group
    
    def form_valid(self, form):
        name = self.object.name
        messages.success(
            self.request,
            f"You successfully deleted the group {name}."
        )
        log_group_activity(
            group=self.request.user.profile.group,
            action="delete_group",
            message=f'{self.request.user.profile.profile_username} deleted "{self.object.name}".'
        )
        return super().form_valid(form)
    

# ======================================================= MEMBER MANAGEMENT =======================================================
class MemberManager(PermissionRequiredMixin, TemplateView):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    template_name = 'groups/user/member_management.html'
    
    def get(self, request):
        group = request.user.profile.group
        gm = GroupMembership.objects.filter(group=group)
        return render(request, self.template_name, {'group_members': gm})
    
class AddMember(PermissionRequiredMixin, TemplateView):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    template_name = 'groups/user/add_member.html'
        
    
class SearchUser(PermissionRequiredMixin, View):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    
    def get(self, request):
        q = request.GET.get('q', '')
        if q == "":
            return JsonResponse({'results': []})
        
        results = MemberManagement.search_user(q, request.user)

        return JsonResponse({'results': results})
    
class InviteUser(PermissionRequiredMixin, View):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    
    def post(self, request):
        try:
            invitee_id = request.POST.get('user_id')
            invitee = get_object_or_404(Profile, id=invitee_id)
            invitor = request.user.profile
            MemberManagement.invite(invitee, invitor)
            
            message = f"Invitation was successfully sent to {invitee.profile_username}."
            type_message = "success"
            
        except GroupErrors as e:
            message = str(e)
            type_message = "danger"
        
        return JsonResponse({
            "message": message,
            "type": type_message
        })

class UserInvitationResponse(PermissionRequiredMixin, View):
    permission_classes = [IsPlayer]
    
    def post(self, request):
        try:
            response = request.POST.get('action')
            notification_id = request.POST.get('notification_id')
            if response == 'accept':
                MemberManagement.invitation_acceptance(notification_id)
            else:
                MemberManagement.invitation_rejection(notification_id)
            
        except Notification.DoesNotExist as e:
            messages.error(request, str(e))
            
        return redirect('user_messages')
        
        
class DeleteMember(PermissionRequiredMixin, View):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    
    def post(self, request):
        selected_members_ids = request.POST.getlist('selected-members')
        try:
            rm = MemberManagement.delete_member(selected_members_ids)
            messages.success(
                request,
                f'{rm} were removed successfully.'
            )
            log_group_activity(
                group=self.request.user.profile.group,
                action="remove_member",
                message=f'{self.request.user.profile.profile_username} removed {rm}.'
            )
            
        except (GroupMembership.DoesNotExist, GroupInvitation.DoesNotExist) as e:
            messages.error(request, str(e))
        return redirect('manage-member')
    
class MemberToLeader(PermissionRequiredMixin, View):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    
    def post(self, request):
        selected_members_ids = request.POST.getlist('selected-members')
        try:
            pl = MemberManagement.assign_member_to_leader(selected_members_ids)
            messages.success(
                request,
                f'{pl} have been promoted to leaders successfully.'
            )
            log_group_activity(
                group=self.request.user.profile.group,
                action="promote_member",
                message=f'{self.request.user.profile.profile_username} promoted "{pl}".'
            )

        except (GroupMembership.DoesNotExist, GroupInvitation.DoesNotExist) as e:
            messages.error(request, str(e))
        return redirect('manage-member')
    


# ========================================================== GROUP ACTIONS ==========================================================
class GroupDashboard(PermissionRequiredMixin, ListView):
    
    """
    Shows the group's members, account summery and activity history.
    """
    permission_classes = [IsPlayer, HasGroup]
    model = GroupActivity
    template_name = 'groups/user/dashboard.html'
    context_object_name = "activities"
    
    def get_queryset(self):
        group = self.request.user.profile.group
        return super().get_queryset().filter(group=group).order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        group = self.request.user.profile.group
        
        context["group"] = group
        context["all_members"] = group.all_members
        context["members"] = group.members
        context["leaders"] = group.leaders
        context["account"] = group.group_account
        return context
    
        
class GroupQuestions(PermissionRequiredMixin, View):
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    template_name = 'groups/user/questions.html'
    
    def get(self, request):
        group_bankaccount = self.request.user.profile.group.group_account
        solved_qs = group_bankaccount.solved_questions
        unsolved_qs = group_bankaccount.unsolved_questions
        return render(request, self.template_name, {'solved_qs': solved_qs,
                                                    'unsolved_qs': unsolved_qs,
                                                    'num_of_solved': solved_qs.count(),
                                                    'num_of_unsolved': unsolved_qs.count()})
    
        
class GroupSettings(PermissionRequiredMixin, UpdateView):
    permission_classes = [IsPlayer, HasGroup, IsGroupLeader]
    model = ContestGroup
    fields = ['name']
    template_name = 'groups/user/settings.html'
    success_url = reverse_lazy('group-dashboard')
    
    def get_object(self):
        group = getattr(self.request.user.profile, 'group', None)
        return get_object_or_404(self.model, pk=group.pk)
    
    def form_valid(self, form):
        messages.success(
            self.request,
            "You successfully changed the group's information."
        )
        log_group_activity(
            group=self.request.user.profile.group,
            action="change_setting",
            message=f"{self.request.user.profile.profile_username} changed group information."
        )
        return super().form_valid(form)
        
class GroupSolveQuestions(PermissionRequiredMixin, UpdateView):
    """
    Handles submitting answers for active group questions.
    """
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    model = GroupQuestion
    fields = ['group_answer']
    template_name = "groups/user/solve_question.html"
    context_object_name = 'group_question'
    
    def get_queryset(self):
        group = self.request.user.profile.group
        return super().get_queryset().filter(account__group=group, is_active=True)
    
    def form_valid(self, form):
        gquestion_obj = form.save()
        tp = TransactionProcessor(self.request.user.profile.group)
        
        try:
            QuestionHandling.check_answer(gquestion_obj, tp)
            
        except GroupQuestionErrors as e:
            messages.error(self.request, str(e))
            return redirect('group-question', pk=gquestion_obj.pk)
        
        messages.success(
            self.request,
            f'Well done! You solved question number {gquestion_obj.question.number}. You received your {gquestion_obj.question.reward_price}π.'
        )
        log_group_activity(
            group=self.request.user.profile.group,
            action="solve_question",
            message=f"+{gquestion_obj.question.reward_price}π | Question #{gquestion_obj.question.number}-{gquestion_obj.question.difficulty} was solved by your group."
        )
        return redirect('group-questions')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.is_solved:
            for field in form.fields.values():
                field.disabled = True
        return form

class GroupItems(PermissionRequiredMixin, View):
    permission_classes = [ CheckContestState, HasGroup]
    template_name = 'groups/user/items.html'
    
    def get(self, request):
        account = self.request.user.profile.group.group_account
        
        queryset = account.items.order_by('-item__current_price')
        q = self.request.GET.get('q')

        if q:
            queryset = queryset.filter(item__name__icontains=q)
            
        return render(request, self.template_name, {'items': queryset,
                                                    'search_input': q})
    
class GroupNotifications(PermissionRequiredMixin, ListView):
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    model = Notification
    ordering = ['-created_at']
    context_object_name = 'notifications'
    template_name = 'groups/user/notifications.html'
    paginate_by = 7
    
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(
                Q(type='group', user=self.request.user.profile) |
                Q(type='contest'),
                is_active=True)
            .order_by("-created_at")
        )