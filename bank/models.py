from django.db import models
from django.db.models import Exists, F, OuterRef, Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError

from groups.models import ContestGroup
from timer.models import TimeControl


# BANK ASSETS
class DifficultyLevel(models.Model):
    """
    Defined for contest manager to set the custom levels.
    """
    difficulty = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    level_buy_price = models.DecimalField(max_digits=10, decimal_places=0)
    level_reward_price = models.DecimalField(max_digits=10, decimal_places=0)
    
    def __str__(self):
        return self.difficulty
    
    @property
    def total_questions(self):
        """Return total number of questions for this difficulty level."""
        return Question.objects.filter(difficulty=self).count()
    
    @property
    def unsold_questions(self):
        """Return number of unsold questions for this difficulty level."""
        return Question.with_owner_status().filter(
            has_owner=False,
            difficulty=self
        ).count()
    
    
class Question(models.Model):
    number = models.PositiveIntegerField(default=0)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True)
    question_prompt = models.TextField()
    answer = models.CharField(max_length=50, blank=False)
    
    def __str__(self):
        return f'{self.difficulty} - {str(self.number)}'
    
    @property
    def buy_price(self):
        """Returns the buy price based on the difficulty level."""
        if self.difficulty:
            return self.difficulty.level_buy_price
        return None
    
    @property
    def reward_price(self):
        """Returns the reward price based on the difficulty level."""
        if self.difficulty:
            return self.difficulty.level_reward_price
        return None
    
    @property
    def level(self):
        return self.difficulty.difficulty if self.difficulty else None
    
    @staticmethod
    def with_owner_status():
        return Question.objects.annotate(
            has_owner=Exists(
                GroupQuestion.objects.filter(
                    question=OuterRef('id'),
                    is_active=True
                )
            )
        )

class Item(models.Model):
    name = models.CharField(max_length=50, blank=False)
    photo = models.ImageField(upload_to='items/', null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return self.name
    
    @staticmethod
    def with_owner_status():
        return Item.objects.annotate(
            has_owner=Exists(
                GroupItem.objects.filter(
                    item=OuterRef('id')
                )
            )
        )
        
    @classmethod
    def reset_items(cls):
        Item.objects.update(
            current_price=F('base_price'),
        )
    

# =================================================== GROUP ASSETS ==============================================================

class BankAccount(models.Model):
    group = models.OneToOneField(ContestGroup, on_delete=models.CASCADE, null=True, related_name='group_account')
    bank_balance = models.DecimalField(max_digits=14, decimal_places=2, default=1000)
    all_items_amounts = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_assets = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_bank = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['is_bank'],
                condition=Q(is_bank=True),
                name='only_one_bank_account'
            )
        ]
        
    def __str__(self):
        if self.group:
            return self.group.name
        return 'Bank'
    
    @classmethod
    def all_bankAccounts(cls):
        return BankAccount.objects.exclude(group=None)
    
    @staticmethod
    def new_bank_account(group):
        ba = BankAccount.objects.create( 
            group=group
        )
        ba.update_total_assets()
        return ba
    
    @property
    def items(self):
        return GroupItem.objects.filter(account=self).order_by('-acquired_at')
    
    @property
    def solved_questions(self):
        return GroupQuestion.objects.filter(account=self, is_active=True, is_solved=True).order_by('-purchase_time')

    @property
    def unsolved_questions(self):
        return GroupQuestion.objects.filter(account=self, is_active=True, is_solved=False).order_by('-purchase_time')
    
    def update_all_items_amounts(self):
        total = GroupItem.objects.filter(account=self).aggregate(s=Sum("item__current_price"))["s"] or 0
        self.all_items_amounts = total
        self.save(update_fields=['all_items_amounts'])
    
    def update_total_assets(self):
        self.total_assets = F('bank_balance') + F('all_items_amounts')
        self.save(update_fields=['total_assets'])
        return self.total_assets
    
    @classmethod
    def get_bank(cls):
        try:
            return cls.objects.get(is_bank=True)
        except ObjectDoesNotExist:
            return None
            
    
class GroupQuestion(models.Model):
    is_active = models.BooleanField(default=True) # Deactivated after trading
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='account_question')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='account_question')
    group_answer = models.CharField(max_length=50, blank=True)
    is_solved = models.BooleanField(default=False)
    
    purchase_time = models.DateTimeField(auto_now_add=True)
    receive_reward_time = models.DateTimeField(null=True, blank=True)
    buy_from = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=0)
    
    def __str__(self):
        sold = 'sold |' if not self.is_active else ''
        return f'{sold} {self.account} -> {self.question.number}-{self.question.difficulty.difficulty}'
        
class ItemAction(models.TextChoices):
    BUY = 'bought', 'Buy'
    SELL = 'sold', 'Sell'
    
class GroupItem(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='account_item')
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='account_item')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=0)
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.item} --> {self.account}'
    
class ItemTransaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='account_item_trans')
    item = models.ForeignKey(GroupItem, on_delete=models.CASCADE, related_name='account_item_trans')
    action = models.CharField(max_length=10, choices=ItemAction.choices, default=ItemAction.BUY)
    inflation_round = models.ForeignKey("Event", on_delete=models.CASCADE)
    action_time = models.DateTimeField(auto_now_add=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f'{self.account.group.name} {self.action} {self.item}'
    
    
# ==================================================== QUESTION TRADES ========================================================

class QuestionTradeStatus(models.TextChoices):
    COMPLETED = 'completed', 'Completed'
    PAYING = 'pending', 'Pending'
    
class QuestionTrade(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    buyer = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='question_buyer', blank=False)
    seller = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='question_seller')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    consensual_price = models.DecimalField(max_digits=12, decimal_places=2, blank=False)
    otp = models.CharField(max_length=6, null=True, blank=False)
    status = models.CharField(max_length=10, choices=QuestionTradeStatus.choices, default=QuestionTradeStatus.PAYING)
    
    def __str__(self):
        return f'{self.seller} sold question {self.question.number} to {self.buyer}'


# ==================================================== BANK EVENTS ========================================================

class BankEventTypes(models.TextChoices):
    INFLATION = 'inflation', 'Inflation'
    INTEREST = 'interest', 'Interest'
    
class Event(models.Model):
    type = models.CharField(max_length=10, choices=BankEventTypes.choices)
    is_positive = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=11, decimal_places=1)
    apply_time = models.DurationField()
    executed = models.BooleanField(default=False)
    
    def __str__(self):
        rate = f'{"-" if not self.is_positive else "+"}{self.rate}%'
        return f'{self.type} | {rate} at {self.apply_time} of the contest.'
    
    def clean(self):
        tc = TimeControl.objects.first()
        if not tc:
            raise ValidationError("You must first define a time control for the contest.")
        if self.apply_time >= tc.duration:
            raise ValidationError("The minute of applying event can't be more than or equal to the duration of the contest.")
        if self.type == 'inflation' and not self.is_positive and self.rate > 100:
            raise ValidationError("Inflation can't be less than -100%.")
        if self.type == 'interest' and not self.is_positive:
            raise ValidationError("Interest must be non-negative.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_event_rate(self):
        if self.is_positive:
            rate = self.rate
        else:
            rate = -self.rate
        return rate
    
    @classmethod
    def reset_events(cls):
        Event.objects.update(
            executed=False,
        )