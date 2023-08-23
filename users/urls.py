
from django.urls import path,include
from users.views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create_user/',CreateUser.as_view()),
    path('login_user/',Login.as_view()),
    path('logout_user/',Logoutview.as_view()),
    path('changepassword/',ChangePassword.as_view()),
    path('resetpasswordlink/',ResetPasswordLink.as_view()),
    path('resetpassword/',UserResetPassword.as_view()),
    path('updateuserandpermissions/',UpdateUserAndPermissions.as_view(), name = 'crud_user'),
    path('getusers/',GetUsersData.as_view(), name = 'crud_user'),
    path('getchips/',GetChips.as_view(), name = 'chips'),
    path('getchipsdata/',GetChipsData.as_view(), name = 'chipsdata'),
    path('updateuserstatus/',UpdateUserStatus.as_view(), name = 'updateuserstatus'),
    path('userdelete/',DeleteUser.as_view()),
    path('getroles/',GetRoles.as_view()),
    path('createbulkusers/',CreateBulkUsers.as_view()),
]
