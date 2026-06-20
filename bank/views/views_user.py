from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView, View, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
import json

from Core.mixins import PermissionRequiredMixin
from Core.permissions import HasGroup, CheckContestState, IsPlayer
from groups.services.group_logs import log_group_activity
from ..models import DifficultyLevel, QuestionTrade, BankAccount, Item
from ..services.transaction_processor import TransactionProcessor
from ..services.otp_processor import OtpProcessor
from ..services.exceptions import BankError, InvalidOTP
from ..services.item_handler import ItemHandler


class BankHome(PermissionRequiredMixin, TemplateView):
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    template_name = 'bank/user/bank.html'

# ===================================================== Bank Transactions =======================================================

# Questions part
class BuyQuestionView(PermissionRequiredMixin, View):
    """
    Allows a player's group to buy a random question from the bank.
    """
    
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    template_name = "bank/user/buy_question.html"
    
    def get(self, request):
        levels = DifficultyLevel.objects.all().order_by('order')
        return render(request, self.template_name, {'levels' : levels})
    
    def post(self, request):
        group = request.user.profile.group
        try:
            level_id = request.POST.get('level_id')
            level = get_object_or_404(DifficultyLevel, id=level_id)
            q = TransactionProcessor(group=group).buy_question_bank(level)
            messages.success(
                request,
                'The question was bought successfully.'
            )
            log_group_activity(
                group=group,
                action="buy_question",
                message=f"-{q.question.buy_price}π | {request.user.profile.profile_username} bought #{q.question.number}-{q.question.level} from the bank.",
            )
            
        except BankError as e:
            messages.error(
                request,
                str(e)
            )
        return redirect('buy-question')
    
# Trade Question part 
class RequestOTP(PermissionRequiredMixin, View):
    """
    Sends a trade OTP to the selected  buyer group's leaders.
    """
    
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    http_method_names = ['post']
    otp_p = OtpProcessor()
    
    def post(self, request, pk):
        data = json.loads(request.body)
        
        buyer_id = data.get("buyer") 
        if not buyer_id:
            return JsonResponse({
            "message": "Please select a group to trade the question with.",
            "type": "danger"
        })
                
        t = 0
        try:
            t = self.otp_p.generate_otp(pk, buyer_id)
            
        except BankError as e:
            message = str(e)
            type = "danger"
            
            return JsonResponse({
                "message": message,
                "type": type
            })
            
        return JsonResponse({
            "message": "OTP was successfully sent.",
            "type": "success",
            "timeout": t
        })
            
class TradeQuestionsView(PermissionRequiredMixin, CreateView):
    """
    Handles question trading between two groups after OTP verification.
    """
    
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    model = QuestionTrade
    fields = ['buyer', 'otp', 'consensual_price']
    template_name = 'bank/user/trade_question.html'
    context_object_name = 'question_trade'
    success_url = reverse_lazy('group-dashboard')
    otp_p = OtpProcessor()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        seller_group = self.request.user.profile.group
        form.fields['buyer'].queryset = BankAccount.objects.exclude(Q(group=seller_group) | Q(is_bank=True))
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        group = self.request.user.profile.group
        question_id = self.kwargs['pk']
        gquestion = get_object_or_404(group.group_account.unsolved_questions, pk=question_id)
        
        ttl = self.otp_p.get_ttl(gquestion.id)
        
        context['gquestion'] = gquestion
        context['group'] = group
        context['otp_remaining_timeout'] = ttl
        return context
    
    def form_valid(self, form):
        group = self.request.user.profile.group
        gquestion_id = self.kwargs['pk']
        obj = form.save(commit=False)
        
        try:
            self.otp_p.verify_otp(obj.otp, gquestion_id)
            tf = TransactionProcessor(group=group).trade_question(obj, gquestion_id)
            messages.success(
                self.request,
                "The question was traded successfully."
            )
            log_group_activity(
                group=group,
                action="trade_question_sell",
                message=f"+{tf.consensual_price}π | {self.request.user.profile.profile_username} sold #{tf.question.number}-{tf.question.level} to {tf.buyer.group.name}."
            )
            log_group_activity(
                group=obj.buyer.group,
                action="trade_question_buy",
                message=f"-{tf.consensual_price}π | You bought #{tf.question.number}-{tf.question.level} from {tf.seller.group.name}."
            )
            
        except InvalidOTP as e:
            messages.error(
                self.request,
                str(e)
            )
            return JsonResponse({"success": False})
        except BankError as e:
            messages.error(
                self.request,
                str(e)
            )
            return JsonResponse({"success": False})
        return redirect('group-dashboard')
    
# Items part
class AllItemsUserView(PermissionRequiredMixin, ListView):
    """
    Shows available and sold items with search and filtering options.
    """
    
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    model = Item
    context_object_name = 'items'
    template_name = 'bank/user/all_items_user.html'
    
    def get_queryset(self):
        queryset = self.model.with_owner_status().order_by(
            'has_owner',
            'current_price'
        )
        
        q = self.request.GET.get('q')
        price = self.request.GET.get('selected-price')
        status = self.request.GET.get('inBank')
        if q or price or status:
            queryset = ItemHandler().search_or_filter(queryset, q, price, status)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = ItemHandler().get_max_min_price()
        
        context['max_price'] = result['max_price']
        context['min_price'] = result['min_price']
        context['search_input'] = self.request.GET.get('q')
        context['selected_price'] = self.request.GET.get('selected-price')
        context['in_bank'] = self.request.GET.get('inBank')
        return context
    
class BuyItemView(PermissionRequiredMixin, View):
    """
    Allows a player's group to buy an available item from the bank.
    """
    
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    
    def post(self, request, pk):
        group = request.user.profile.group
        item_id = pk
        
        try:
            gi = TransactionProcessor(group=group).buy_item(item_id)
            messages.success(
                self.request,
                f"{gi.item.name} was bought successfully."
            )
            log_group_activity(
                group=group,
                action="buy_item",
                message=f"-{gi.item.current_price}π | {self.request.user.profile.profile_username} bought {gi.item.name}."
            )
            
        except BankError as e:
            messages.error(
                self.request,
                str(e)
            )
        return redirect('items-user')

class SellItemView(PermissionRequiredMixin, View):
    """
    Allows a player's group to sell one of its items back to the bank.
    """
    
    permission_classes = [IsPlayer, CheckContestState, HasGroup]
    
    def post(self, request, pk):
        group = request.user.profile.group
        groupitem_id = pk
        
        try:
            it = TransactionProcessor(group=group).sell_item(groupitem_id)
            messages.success(
                self.request,
                f'{it.item.item.name} was sold successfully. You received your {it.paid_amount}π.'
            )
            log_group_activity(
                group=group,
                action="sell_item",
                message=f'+{it.item.item.current_price}π | {self.request.user.profile.profile_username} sold "{it.item.item.name}" to the bank.'
            )
            
        except BankError as e:
            messages.error(
                self.request,
                str(e)
            )
        return redirect('group-items')    