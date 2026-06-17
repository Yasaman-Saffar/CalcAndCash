from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.utils import timezone
from django.urls import reverse_lazy

from Core.mixins import PermissionRequiredMixin
from Core.permissions import IsStaff
from ..models import Question, Item, DifficultyLevel
from ..services.question_handler import QuestionHandler
from ..services.item_handler import ItemHandler

#=========================================================== Question Handling(staff) ==============================================================

class AllQuestions(PermissionRequiredMixin, ListView):
    """
    Staff view for listening questions with search and filtering options.
    """
    
    permission_classes = [IsStaff]
    model = Question
    context_object_name = 'questions'
    template_name = 'bank/staff/questions/list.html'
    
    def get_queryset(self):
        queryset = self.model.with_owner_status().order_by(
            'difficulty__order', 'number'
        )
        
        q = self.request.GET.get('q')
        difficulties = self.request.GET.getlist('difficulty')
        status = self.request.GET.get('inBank')
        handler = QuestionHandler()
        
        if q:
            queryset = handler.search_question(q, queryset)
        if difficulties:
            queryset = handler.filter_difficulty(difficulties, queryset)
        if status:
            queryset = handler.filter_bank_status(status, queryset)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['difficulties'] = DifficultyLevel.objects.all().order_by("order")
        context['filtered_difficulties'] = self.request.GET.getlist('difficulty')
        context['in_bank'] = self.request.GET.get('inBank')
        return context

class QuestionDetails(PermissionRequiredMixin, DetailView):
    permission_classes = [IsStaff]
    model = Question
    template_name = 'bank/staff/questions/details.html'
    context_object_name = 'question'


class AddQuestion(PermissionRequiredMixin, CreateView):
    permission_classes = [IsStaff]
    model = Question
    fields = ['number', 'difficulty', 'question_prompt', 'answer']
    template_name = 'bank/staff/questions/create.html'
    context_object_name = 'form'
    success_url = reverse_lazy('add-new-question')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if 'difficulty' in form.fields:
            form.fields['difficulty'].queryset = form.fields['difficulty'].queryset.order_by('order')
        return form
    
    def form_valid(self, form):
        form.instance.editors_history = {}
        form.instance.editors_history[self.request.user.phone] = f'Created at {timezone.now().isoformat()}'
        
        number = form.instance.number
        difficulty = form.instance.level
        messages.success(
            self.request,
            f'Question number {number} ({difficulty}) was added successfully.'
        )
        return super().form_valid(form)
    

class EditQuestion(PermissionRequiredMixin, UpdateView):
    permission_classes = [IsStaff]
    model = Question
    fields = ['number', 'difficulty', 'question_prompt', 'answer']
    template_name = 'bank/staff/questions/edit.html'
    context_object_name = 'form'
    success_url = reverse_lazy('questions')
    
    def form_valid(self, form):
        number = form.instance.number
        difficulty = form.instance.level
        messages.success(
            self.request,
            f'Question number {number} ({difficulty}) was edited successfully.'
        )
        return super().form_valid(form)
    
    
class DeleteQuestion(PermissionRequiredMixin, DeleteView):
    permission_classes = [IsStaff]
    model = Question
    success_url = reverse_lazy('questions')

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        number = obj.number
        difficulty = obj.level

        messages.success(
            request,
            f'Question number {number} ({difficulty}) was deleted successfully .'
        )
        return super().post(request, *args, **kwargs)
    
# ===================================================== Item Handling(staff) ====================================================
class AllItemsStaff(PermissionRequiredMixin, ListView):
    """
    Staff view for listing items with search, price and bank-status filters.
    """
    
    permission_classes = [IsStaff]
    model = Item
    context_object_name = 'items'
    template_name = 'bank/staff/items/list.html'

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
    
    
class AddItem(PermissionRequiredMixin, CreateView):
    permission_classes = [IsStaff]
    model = Item
    fields = ['name', 'photo', 'base_price']
    template_name = 'bank/staff/items/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('add-new-item')

    def form_valid(self, form):
        form.instance.current_price = form.instance.base_price
        messages.success(
            self.request,
            f'{form.instance.name} was added successfully.'
        )
        return super().form_valid(form)
    
    
class EditItem(PermissionRequiredMixin, UpdateView):
    permission_classes = [IsStaff]
    model = Item
    fields = ['name', 'photo', 'base_price']
    template_name = 'bank/staff/items/edit.html'
    context_object_name = 'item'
    success_url = reverse_lazy('items-staff')
    
    def form_valid(self, form):
        form.instance.current_price = form.instance.base_price
        messages.success(
            self.request,
            f'{form.instance.name} was edited successfully.'
        )
        return super().form_valid(form)


class DeleteItem(PermissionRequiredMixin, DeleteView):
    permission_classes = [IsStaff]
    model = Item
    success_url = reverse_lazy('items-staff')

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.name

        messages.success(
            request,
            f'{name} was deleted successfully.'
        )
        return super().post(request, *args, **kwargs)