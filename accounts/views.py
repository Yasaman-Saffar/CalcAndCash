
import time
from django.views.generic import View, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from allauth.account.views import SignupView
from allauth.account import app_settings
from allauth.account.stages import LoginByCodeStage, LoginStageController
from allauth.account.views import ConfirmLoginCodeView as BaseConfirmLoginCodeView
from allauth.account.views import _VerifyPhoneSignupView, _VerifyPhoneChangeView
from allauth.account.stages import PhoneVerificationStage

from .models import Profile

class PlayerSignupView(SignupView):
    template_name = "account/signup.html"
    
class StaffSignupView(SignupView):
    template_name = "account/signup.html"

    def dispatch(self, request, *args, **kwargs):
        request.is_staff_signup = True
        return super().dispatch(request, *args, **kwargs)
    
class CompleteInformation(UpdateView):
    model = Profile
    fields = [
        'profile_username', 
        'first_name', 
        'last_name', 
        'national_id', 
        'date_of_birth', 
        'gender', 
        'avatar'
    ]
    template_name = 'dashboard/update_information.html'
    success_url = reverse_lazy('dashboard')
    
    def get_object(self):
        return get_object_or_404(self.model, pk=self.request.user.profile.pk)

class ConfirmLoginCodeView(BaseConfirmLoginCodeView):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        
        # Show remaining OTP time in the template
        sent_at = self._process.state.get("at", 0)
        timeout = settings.ACCOUNT_PHONE_VERIFICATION_TIMEOUT
        
        elapsed = int(time.time() - sent_at)
        remaining = max(0, timeout - elapsed)
        
        ret["code_remaining"] = remaining
        return ret

confirm_login_code = ConfirmLoginCodeView.as_view()

class VerifyPhoneSignupView(_VerifyPhoneSignupView):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        sent_at = self.process.state.get("at", 0)
        timeout = settings.ACCOUNT_PHONE_VERIFICATION_TIMEOUT
        elapsed = int(time.time() - sent_at)
        ret["code_remaining"] = max(0, timeout - elapsed)
        return ret

class VerifyPhoneChangeView(_VerifyPhoneChangeView):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        sent_at = self.process.state.get("at", 0)
        timeout = settings.ACCOUNT_PHONE_VERIFICATION_TIMEOUT
        elapsed = int(time.time() - sent_at)
        ret["code_remaining"] = max(0, timeout - elapsed)
        return ret

def verify_phone(request):
    if request.user.is_authenticated:
        return VerifyPhoneChangeView.as_view()(request)
    return VerifyPhoneSignupView.as_view()(request)

class CancelVerifyPhoneView(View):
    def get(self, request, *args, **kwargs):
        # print("hiiiiiiiii")
        stage = LoginStageController.enter(request, PhoneVerificationStage.key)
        # print("STAGE:", stage)
        # print("SESSION KEYS:", list(request.session.keys()))
        if stage:
            stage.abort()
        return HttpResponseRedirect(reverse("account_login"))

class CancelLoginCodeView(View):
    def get(self, request, *args, **kwargs):
        
        # Abort the current login-by-code stage and return user to login flow
        stage = LoginStageController.enter(request, LoginByCodeStage.key)

        if stage:
            stage.abort()

        next_url = request.GET.get("next")

        if next_url == "code":
            return HttpResponseRedirect(reverse("account_request_login_code"))

        return HttpResponseRedirect(reverse("account_login"))