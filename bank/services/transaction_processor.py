from django.db import transaction
from django.db.models import F
from ..models import GroupQuestion, GroupItem, ItemTransaction, Item, BankAccount
from .question_handler import QuestionHandler
from .exceptions import BankError, InsufficientFundsError, InsufficientQuestionsError, ItemDoesNotExist, QuestionDoesNotExist
from timer.models import TimeControl

class TransactionProcessor:
    """
    Handles contest transactions such as 
    buying questions, solving questions, 
    trading questions and buying or selling items.
    """
    
    def __init__(self, group, q_handler=None, i_handler=None):
        self.account = group.group_account
        self.qh = q_handler or QuestionHandler()
    
    def _check_enough_asset(self, price, account=None):
        if not account:
            account = self.account 
        return price <= account.bank_balance
    
    def _create_new_ownership_question(self, buyer, buy_from, question, price):
        return GroupQuestion.objects.create(
            account=buyer,
            question=question,
            buy_from=buy_from,
            paid_amount=price
        )
    
    def _create_new_ownership_item(self, item, price):
        return GroupItem.objects.create(
            item=item,
            account=self.account,
            paid_amount=price
        )
    
    def _save_item_transaction(self, gitem, action='bought'):
        timer = TimeControl.objects.first()
        return ItemTransaction.objects.create(
            account=self.account,
            item=gitem,
            action=action,
            inflation_round=timer.current_inflation,
            paid_amount=gitem.item.current_price,
        )
                
    def _pay_money(self, price):
        self.account.bank_balance = F('bank_balance') - price
        self.account.save(update_fields=['bank_balance'])
        
    def _credit_money(self, price):
        self.account.bank_balance = F('bank_balance') + price
        self.account.save(update_fields=['bank_balance'])
    
    def _deactivate_old_question(self, gquestion):
        gquestion.is_active = False
        gquestion.save()
        
    def _transfer_money(self, buyer, seller, price):
        buyer.bank_balance = F('bank_balance') - price
        seller.bank_balance = F('bank_balance') + price
        
        buyer.save(update_fields=['bank_balance'])
        buyer.update_total_assets()
        
        seller.save(update_fields=['bank_balance'])
        seller.update_total_assets()
        
    def _save_trade(self, trade_form, seller, question):
        trade_form.seller = seller
        trade_form.question = question
        trade_form.status = "completed"
        trade_form.save()
        
        
        
    @transaction.atomic
    def buy_question_bank(self, level):
        """
        Buy a random available question from
        the bank for the selected level.
         
        The method locks the selected question, 
        charges the buyer, creates ownership and 
        recalculates total assets.
        """
        level_price = level.level_buy_price
        buyer = self.account
        buy_from = BankAccount.get_bank()
        
        if not self._check_enough_asset(level_price):
            raise InsufficientFundsError("You don't have enough bank balance to buy this question.")
        
        question = self.qh.get_random_question(level)
        if not question:
            raise InsufficientQuestionsError(f'We have run out of {level.difficulty} questions. You could trade with other groups.')
        
        new_gq = self._create_new_ownership_question(buyer, buy_from, question, level_price)
        self._pay_money(level_price)
        buyer.update_total_assets()
    
        return new_gq
    
    @transaction.atomic
    def process_answer(self, group_question):
        """
        Check the submitted answer and reward the group if it is correct.
        """
        
        if self.qh.question_answer_checker(group_question):
            self.receive_question_reward(group_question)
            self.qh.update_group_question(group_question)
            return True
        return False
        
    @transaction.atomic
    def receive_question_reward(self, group_question):
        price = group_question.question.difficulty.level_reward_price
        self._credit_money(price)
        self.account.update_total_assets()
    
    @transaction.atomic    
    def trade_question(self, trade_form, gquestion_id):
        """
        Complete a question trade between two groups.

        The old question ownership is deactivated, a new ownership record is
        created for the buyer, money is transferred, and the trade is marked completed.
        """
        
        try:
            gquestion = self.account.unsolved_questions.select_for_update().get(pk=gquestion_id)
        except GroupQuestion.DoesNotExist:
            raise QuestionDoesNotExist("Question not available.")
        
        buyer = trade_form.buyer
        seller = gquestion.account
        price = trade_form.consensual_price
        question = gquestion.question
        
        if not self._check_enough_asset(price, buyer):
            raise InsufficientFundsError(f"{buyer.group.name} doesn't have enough bank balance to buy this question.")
        
        self._deactivate_old_question(gquestion)
        new_gq = self._create_new_ownership_question(buyer, seller,  question, price)
        self._transfer_money(buyer, seller, price)
        self._save_trade(trade_form, seller, question)
        
        return trade_form
        
    @transaction.atomic
    def buy_item(self, item_id):
        """
        Buy an available item from the bank and update the group's assets.
        """
        
        try:
            item = Item.with_owner_status().select_for_update().get(id=item_id)
        except Item.DoesNotExist:
            raise ItemDoesNotExist("Item not available.")
        if item.has_owner:
            raise BankError(f'{item.name} was already sold.')
        
        price = item.current_price
        if not self._check_enough_asset(price):
            raise InsufficientFundsError(f"You don't have enough bank balance to buy {item.name}.")
        
        self._pay_money(price)
        gi = self._create_new_ownership_item(item, price)
        self._save_item_transaction(gi)
        self.account.update_all_items_amounts()
        self.account.update_total_assets()
        
        return gi
    
    @transaction.atomic
    def sell_item(self, groupitem_id):
        """
        Sell a group-owned item back to the bank and update the group's assets.
        """
        
        try:
            groupitem = self.account.items.select_for_update().get(id=groupitem_id)
        except GroupItem.DoesNotExist:
            raise ItemDoesNotExist("Item not available.")
        
        price = groupitem.item.current_price
        
        it = self._save_item_transaction(groupitem, action='sold')
        groupitem.delete()
        self._credit_money(price)
        self.account.update_all_items_amounts()
        self.account.update_total_assets()
        
        return it