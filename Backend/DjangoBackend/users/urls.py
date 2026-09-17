from django.urls import path
from users.views import UserView

urlpatterns = [
    path("profile/", UserView.as_view())
]
