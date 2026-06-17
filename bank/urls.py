from django.urls import path
from .views import views_staff, views_user

urlpatterns = [
    # Staff"s part
    path('all-questions/', views_staff.AllQuestions.as_view(), name='questions'),
    path('question/<int:pk>', views_staff.QuestionDetails.as_view(), name='question-detail'),
    path('add-question/', views_staff.AddQuestion.as_view(), name='add-new-question'),
    path('edit-question/<int:pk>', views_staff.EditQuestion.as_view(), name='edit-question'),
    path('delete-question/<int:pk>', views_staff.DeleteQuestion.as_view(), name='delete-question'),
    
    path('all-items-staff/', views_staff.AllItemsStaff.as_view(), name='items-staff'),
    path('add-item/', views_staff.AddItem.as_view(), name='add-new-item'),
    path('edit-item/<int:pk>', views_staff.EditItem.as_view(), name='edit-item'),
    path('delete-item/<int:pk>', views_staff.DeleteItem.as_view(), name='delete-item'),
    
    # Players' part
    path('marketplace/', views_user.BankHome.as_view(), name='bank-marketplace'),
    path('buy-question/', views_user.BuyQuestionView.as_view(), name='buy-question'),
    path('trade-question/<int:pk>', views_user.TradeQuestionsView.as_view(), name='trade-question'),
    path('trade-question/request-otp/<int:pk>', views_user.RequestOTP.as_view(), name='otp-request'),
    
    path('all-items-user/', views_user.AllItemsUserView.as_view(), name='items-user'),
    path('buy-item/<int:pk>', views_user.BuyItemView.as_view(), name='buy-item'),
    path('sell-item/<int:pk>', views_user.SellItemView.as_view(), name='sell-item'),
]
