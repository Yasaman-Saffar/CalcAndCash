from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.PlayerSignupView.as_view(), name="account_signup"),
    path("staff-signup/", views.StaffSignupView.as_view(), name="account_staff_signup"),
    path('profile/', views.CompleteInformation.as_view(), name="profile"),
    
    path("phone/verify/", views.verify_phone, name="account_verify_phone"),
    path("phone/cancel-verify/", views.CancelVerifyPhoneView.as_view(), name="account_cancel_verify_phone"),
    path("login/code/confirm/", views.confirm_login_code, name="account_confirm_login_code"),
    path("login/code/cancel/", views.CancelLoginCodeView.as_view(), name="account_cancel_login_code"),
]