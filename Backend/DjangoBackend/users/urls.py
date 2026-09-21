from django.urls import path
from users.views import UserView
from users.views import UserLastMessageAtView
from users.views import UsersLastMessageAtView

urlpatterns = [
    path("profile/", UserView.as_view()),
    path("get_users_last_message_at/", UsersLastMessageAtView.as_view()),
    path("get_user_last_message_at/", UserLastMessageAtView.as_view()),
]
