import requests
import logging
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.internal.cryptokit import generate_user_code
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from .forms import CustomPhoneField

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomDefaultAccountAdapter(DefaultAccountAdapter):
    
    def phone_form_field(self, **kwargs):
        return CustomPhoneField(**kwargs)
    
    def clean_phone(self, phone):
        """
        Validate phone uniqueness depending on the current allauth flow:
        login, signup or phone change.
        """
        if self.request and 'login' in self.request.path:
            user = self.get_user_by_phone(phone)
            if user:
                return phone
            else:
                raise ValidationError('The phone number is not registered.')
        if self.request and 'signup' in self.request.path:
            if User.objects.filter(phone=phone).exists():
                raise ValidationError('This phone number has already registered.')
            return phone
        if self.request and 'phone/change' in self.request.path:
            if self.request.user.phone == phone:
                raise ValidationError('This is your current phone number!')
            if User.objects.filter(phone=phone).exists():
                raise ValidationError('This phone number is already in use.')
            return phone
        
        return phone
        
    def set_phone(self, user, phone: str, verified: bool):
        user.phone = phone
        user.phone_verified = verified
        user.save()

    def get_phone(self, user):
        return user.phone, user.phone_verified
    
    def set_phone_verified(self, user, phone: str):
        # Keep previous phone number when the user changes their verified phone.
        if not self.request.user.is_anonymous and self.request.user.phone != phone:
            if not user.phone_history:
                user.phone_history = {}
            user.phone_history[user.phone]=timezone.now().isoformat()
            user.phone = phone
        user.phone_verified = True
        user.save()

    def get_user_by_phone(self, phone: str):
        try:
            return User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None
        
    def send_unknown_account_sms(self, phone: str, **kwargs) -> None:
        pass

    def send_verification_code_sms(self, user, phone: str, code: str, **kwargs):
        """
        Send allauth-generated verification code through the SMS provider.
        """
        if settings.DEBUG:
            print(f"CALC AND CASH | Your verification code is: {code}")
            return {"success": True, "debug": True}
            
        else:
            data = {
                "from": settings.SMS_FROM_NUMBER,
                "to": phone,
                "text": f"CALC AND CASH | Your verification code is: {code}",
            }

            try:
                response = requests.post(
                    settings.SMS_API_URL,
                    json=data,
                )

                response.raise_for_status()

                result = response.json()

                if result.get("recId"):
                    logger.info(
                        f"OTP SMS sent successfully to {phone}. "
                        f"recId={result['recId']}"
                    )

                    return {
                        "success": True,
                        "recId": result["recId"],
                    }

                error_message = result.get(
                    "status",
                    "SMS provider returned unknown error."
                )

                logger.error(
                    f"SMS sending failed for {phone}. "
                    f"Provider error: {error_message}"
                )

                return {
                    "success": False,
                    "error": error_message,
                }

            except requests.Timeout:
                logger.error(
                    f"SMS sending timeout for {phone}."
                )

                return {
                    "success": False,
                    "error": "SMS provider timeout.",
                }

            except requests.ConnectionError:
                logger.error(
                    f"SMS provider connection error for {phone}."
                )

                return {
                    "success": False,
                    "error": "Could not connect to SMS provider.",
                }

            except requests.HTTPError as e:
                logger.error(
                    f"SMS provider HTTP error for {phone}: {e}"
                )

                return {
                    "success": False,
                    "error": f"HTTP Error: {e}",
                }

            except requests.RequestException as e:
                logger.exception(
                    f"Unexpected SMS error for {phone}"
                )

                return {
                    "success": False,
                    "error": str(e),
                }
    
    def generate_phone_verification_code(self, *, user, phone: str) -> str:
        """
        Generates a 6-digit numeric phone verification code for allauth.
        """
        return generate_user_code(length=6, numeric=True)