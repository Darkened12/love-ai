from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    Creates a new user account using `RegisterSerializer`.

    Authentication is not required, allowing new users to register
    without an existing account.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login endpoint.

    Authenticates the user with their credentials and returns an
    access token and a refresh token using the customized serializer,
    which includes the `user_id` claim.
    """

    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    """
    JWT refresh endpoint.

    Receives a valid refresh token and returns a new access token,
    allowing the client to remain authenticated without requiring
    the user to log in again.
    """

    pass