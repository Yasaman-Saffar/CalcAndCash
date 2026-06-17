from django.db.models import F, OuterRef, Sum, Subquery, Value
from django.db.models.functions import Coalesce, Round
from bank.models import BankAccount, Item, GroupItem
from realtime.notif_services.notif_handling import NotifHandling
from realtime.services import inflation_announcement
from timer.models import TimeControl

class EconomyEngine:
    """
    Handles ecofnomy events during the contest,
    including inflation, bank interest,
    asset recalculation and player notifications.
    """
    
    def _event_information(self, event):
        type = event.type
        rate = event.rate
        is_positive = event.is_positive
        return type, rate, is_positive
     
    def apply_inflation(self, event):
        """
        Apply an inflation event to item prices,
        recalculation team assets, notify players,
        and update the current inflation state.
        """
        
        type, rate, is_positive = self._event_information(event)

        inflation_rate = self._calculate_multiplier(rate, is_positive)
        self._inflation_on_items(inflation_rate)
        self._bank_accounts_update_inflation()
        
        header, message = self._create_message(type, rate, is_positive)
        self._notify_players('contest', 'bank-event', header, message, event)

        self._save_current_inflation(event)
        
        self._change_inflation_rate_socket(event)
    

    def apply_interest(self, event):
        """
        Apply bank interest to all
        team bank accounts and notify players.
        """
        
        type, rate, is_positive = self._event_information(event)
        
        interest_rate = self._calculate_multiplier(rate, is_positive)
        self._bank_accounts_update_interest(interest_rate)

        header, message = self._create_message(type, rate, is_positive)
        self._notify_players('contest', 'bank-event', header, message, event)
        
        
    def _calculate_multiplier(self, rate, is_positive):
        if is_positive:
            rate = (100 + rate) / 100
        else:
            rate = (100 - rate) / 100
            
        return rate
    
    def _inflation_on_items(self, inflation_rate):
        Item.objects.update(
            current_price=Round(F('current_price') * inflation_rate, 2)
        )
        
    def _bank_accounts_update_inflation(self):
        """ 
        Recalculate each team's item value and
        total assets after item prices change.
        """
        
        item_sum = GroupItem.objects.filter(account=OuterRef("pk")).values("account").annotate(s=Sum("item__current_price")).values("s")
        BankAccount.all_bankAccounts().update(
            all_items_amounts=Coalesce(Subquery(item_sum), Value(0)),
            total_assets=F("bank_balance") + Coalesce(Subquery(item_sum), Value(0))
        )
    
    def _bank_accounts_update_interest(self, interest_rate):
        """ 
        Update bank balances after interest and refresh total assets.
        """
        
        BankAccount.all_bankAccounts().update(
            bank_balance=Round(F('bank_balance') * interest_rate, 2),
            total_assets=Round(F('bank_balance') * interest_rate, 2) + F('all_items_amounts')
        )
    
    def _create_message(self, type, rate, is_positive):
        # Inflation messages
        if type == "inflation": 
            if is_positive:
                header = f"Inflation ▲ {rate}%"
                message = f"The cost of goods has risen by {rate}%. Time to cash in and sell? Or wait it out for even higher gains?"
            else:
                header = f"Inflation ▼ {rate}%"
                message = f"Prices have dipped by {rate}%. Everything is getting cheaper! Time to buy, or wait for the bottom?"
                
        # Interest messages
        else:                   
            header = "Profit Earned!"
            message = f"Good news! A {rate}% profit was just added to your bank account. Your balance is growing!"
            
        return header, message
            
        
    def _notify_players(self, type, context, header, message, event):
        NotifHandling.contest_message(
            type=type,
            context=context,
            header=header,
            message=message,
            content_object=event
        )
        
    def _save_current_inflation(self, event):
        """ 
        Store the latest inflation event 
        so active contest pages can show it.
        """
        
        timer = TimeControl.objects.first()
        timer.set_current_inflation(event)
    
    def _change_inflation_rate_socket(self, event):
        inflation_announcement({
            "rate": str(event.get_event_rate())
        })