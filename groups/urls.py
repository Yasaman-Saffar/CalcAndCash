from django.urls import path
from .views import views_user, views_staff


urlpatterns = [
    # Staff"s part
    path('all/', views_staff.AllGroups.as_view(), name="groups"),
    path('info/<int:pk>/', views_staff.GroupDetails.as_view(), name="group-info"),
    
    
    # Players' part
    path('add-new-group/', views_user.AddGroup.as_view(), name='add_group'),
    
    path('manage-member/', views_user.MemberManager.as_view(), name='manage-member'),
    path('add-member/', views_user.AddMember.as_view(), name='add-member'),
    path('add-member/search-user/', views_user.SearchUser.as_view(), name='search-user'),
    path('add-member/invite/', views_user.InviteUser.as_view(), name='invite-user'),
    path('invitation-response/', views_user.UserInvitationResponse.as_view(), name='user-invitation-response'),
    path('delete-member/', views_user.DeleteMember.as_view(), name='delete-member'),
    path('promote-to-leader/', views_user.MemberToLeader.as_view(), name='promote-member'),
    
    path('settings/', views_user.GroupSettings.as_view(), name='group-settings'),
    path('delete-group/', views_user.DeleteGroup.as_view(), name='group-delete'),
    
    path('dashboard/', views_user.GroupDashboard.as_view(), name='group-dashboard'),
    path('questions/', views_user.GroupQuestions.as_view(),name='group-questions'),
    path('items/', views_user.GroupItems.as_view(), name='group-items'),
    path('messages/', views_user.GroupNotifications.as_view(), name='group-notifs'),
    path('question/<int:pk>', views_user.GroupSolveQuestions.as_view(), name='group-question'),
    
]
