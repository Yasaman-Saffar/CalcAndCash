import random
from django.conf import settings

from bank.models import BankAccount
from realtime.notif_services.notif_handling import NotifHandling
from .exceptions import InvalidOTP, NotExpiredOTP, GroupDoesNotExist, NoLeaderFound


class OtpProcessor:
    """
    Handles OTP generation, storage, delivery 
    and verification for group question trading. 
    """
    
    redis_client = settings.REDIS_OTP
    OTP_EXPIRE_SECONDS = 75
    
    def check_last_otp(self, pk, buyer_id):
        key = f"trade_otp_gquestion:{pk}"
        stored_otp = self.redis_client.get(key)
        if stored_otp:
            buyer = BankAccount.all_bankAccounts().get(id=buyer_id)
            raise NotExpiredOTP(f"Your group's last otp hasn't expired yet. It's a trade with group '{buyer.group.name}'.")
    
    def generate_otp(self, pk, buyer_id):
        """
        Generate and send a new OTP for a question trade.
        """
        
        self.check_last_otp(pk, buyer_id)
        otp = str(random.randint(100000, 999999))
        self.save_otp(pk, otp)
        self.notify_otp(otp, buyer_id)
        return self.OTP_EXPIRE_SECONDS
    
    def save_otp(self, pk, otp):
        self.redis_client.setex(
            f"trade_otp_gquestion:{pk}",
            self.OTP_EXPIRE_SECONDS,
            otp
        )
    
    def find_leaders(self, buyer_id):
        """
        Return buyer group leaders who should recieve the trade OTP.
        """
        
        try:
            buyer_account = BankAccount.all_bankAccounts().select_for_update().get(pk=buyer_id)
        except BankAccount.DoesNotExist:
            raise GroupDoesNotExist("Buyer group does not exist.")
        
        leaders = buyer_account.group.leaders
        if not leaders.exists():
            raise NoLeaderFound(f"{buyer_account.name} does not have any leader to send the otp to!")
        return leaders
    
    def notify_otp(self, otp, buyer_id):
        leaders = self.find_leaders(buyer_id)
        header = "New OTP code"
        message = f"OTP for your group transaction: {otp}"
        
        NotifHandling.notify_message(type='group',context='otp', users=leaders, header=header, message=message) 
            
    def get_ttl(self, pk):
        key = f"trade_otp_gquestion:{pk}"
        ttl = self.redis_client.ttl(key)
        ttl = max(0, ttl)
        return ttl
    
    def verify_otp(self, entered_otp, gquestion_id):
        """
        Verify a submitted OTP and invalidate it after successful use.
        """
        
        key = f"trade_otp_gquestion:{gquestion_id}"
        stored_otp = self.redis_client.get(key)
        
        if stored_otp != entered_otp:
            raise InvalidOTP("Invalid or expired OTP.")
        
        self.redis_client.delete(key)