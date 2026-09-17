# authentication/urls.py
from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, MyTokenRefreshView
urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("token/", MyTokenObtainPairView.as_view()),
    path("token/refresh/", MyTokenRefreshView.as_view()),
]
