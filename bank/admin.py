from django.contrib import admin
from django import forms
from django.db.models import Count, Q, Exists, OuterRef
from .models import DifficultyLevel, Question, GroupQuestion, GroupItem, BankAccount, QuestionTrade, Item, ItemTransaction, Event

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    model = BankAccount
    list_select_related = ('group',)
    list_display = ('group__name', 'total_assets')
    search_fields = ('group__name',)
    
@admin.register(DifficultyLevel)
class DifficultyAdmin(admin.ModelAdmin):
    model = DifficultyLevel
    list_display = ('order', 'difficulty', 'unsold', 'level_buy_price', 'level_reward_price', 'total')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_count=Count("question"),
            unsold_count=Count('question', filter=~Exists(GroupQuestion.objects.filter(
                question=OuterRef('question__id')
            )))
        )
    
    def unsold(self, obj):
        return obj.unsold_count
    
    def total(self, obj):
        return obj.total_count
    
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'apply_time': forms.TextInput(attrs={
                'placeholder': 'For example 00:01:30'
            })
        }
        
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ('__str__', 'executed')
    ordering = ('apply_time',)
    list_filter = ('type', 'executed')
    search_fields = ('type',)
    
@admin.register(GroupItem)
class GroupItemAdmin(admin.ModelAdmin):
    model = GroupItem
    list_display = ('item', 'account', 'acquired_at')
    search_fields = ('item__name', 'account__group__name')
    
@admin.register(GroupQuestion)
class GroupQuestionAdmin(admin.ModelAdmin):
    model = GroupQuestion
    list_display = ('__str__','is_active' , 'question__difficulty', 'account', 'is_solved', 'purchase_time')
    ordering = ('-is_active', 'purchase_time')
    list_filter = ('is_active', 'is_solved', 'question__difficulty')
    search_fields = ('question__number', 'account__group__name', 'question__difficulty')

@admin.register(ItemTransaction)
class ItemTransactionAdmin(admin.ModelAdmin):
    model = ItemTransaction
    list_display = ('item','account' , 'action', 'inflation_round', 'action_time')
    ordering = ('action_time',)
    list_filter = ('action', 'inflation_round',)
    search_fields = ('item__name', 'account__group__name')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    model = Item
    list_display = ('name','current_price' , 'base_price', 'in_bank')
    list_filter = ('current_price',)
    search_fields = ('item__name', 'account__group__name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            sold=Exists(
                GroupItem.objects.filter(
                    item=OuterRef('pk'),
            )
        )
    )
        
    @admin.display(boolean=True, description="In Bank")
    def in_bank(self, obj):
        return not obj.sold

@admin.register(QuestionTrade)
class QuestionTradeAdmin(admin.ModelAdmin):
    model = QuestionTrade
    list_display = ('question__number', 'status', 'seller', 'buyer', 'consensual_price')
    ordering = ('created_at',)
    search_fields = ('question__number', 'buyer', 'seller')
    list_filter = ('status',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_select_related = ('difficulty',)
    list_display = ('number', 'difficulty', 'sold')
    search_fields = ('difficulty', 'number')
    list_filter = ('difficulty',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            sold=Exists(
                GroupQuestion.objects.filter(
                    question=OuterRef('pk'),
                    is_active=True
                )
            )
        )

    @admin.display(boolean=True, description="Is Sold")
    def sold(self, obj):
        return obj.sold
    
    
    
    







