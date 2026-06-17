from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from allauth.account.adapter import get_adapter
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        
        if getattr(request, "is_staff_signup", False):
            user.is_staff = True
            user.save()

        return user

class CustomPhoneField(forms.CharField):
    e164_validator = RegexValidator(
        regex=r"^(\+\d+{1-3})?\d{11,13}",
        message=_("Enter a valid phone number."),
        code="invalid_phone",
    )

    def __init__(self, *args, **kwargs):
        widget = forms.TextInput(
            attrs={"placeholder": _("Phone"), "autocomplete": "tel", "type": "tel"}
        )
        kwargs.setdefault("validators", [self.e164_validator])
        kwargs.setdefault("widget", widget)
        kwargs.setdefault("label", _("Phone"))
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        if value:
            value = value.replace(" ", "").replace("-", "")
            value = get_adapter().clean_phone(value)
        return value