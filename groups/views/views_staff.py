from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from bank.models import BankAccount
from Core.permissions import IsStaff
from Core.mixins import PermissionRequiredMixin


class AllGroups(PermissionRequiredMixin, ListView):
    permission_classes = [IsStaff]
    model = BankAccount
    template_name = "groups/staff/list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["accounts"] = self.model.all_bankAccounts()
        return context

class GroupDetails(PermissionRequiredMixin, DetailView):
    permission_classes = [IsStaff]
    model = BankAccount
    context_object_name = "account"
    template_name = "groups/staff/details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        account = get_object_or_404(BankAccount, id=self.kwargs['pk'])
        
        context["s_questions"] = account.solved_questions
        context["uns_questions"] = account.unsolved_questions
        context["items"] = account.items
        
        context["leaders"] = account.group.leaders
        context["members"] = account.group.members
        return context