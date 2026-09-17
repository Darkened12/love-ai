from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer responsible for registering new users.

    Exposes only the fields required to create an account (`username` and
    `password`), while keeping the user ID read-only.

    The password is securely stored using Django's `set_password()`, which
    applies the configured password hashing algorithm.
    """

    class Meta:
        model = User
        fields = ("id", "username", "password")
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        """
        Creates a new user with a hashed password.

        Args:
            validated_data: Data already validated by the serializer.

        Returns:
            User: The newly created and saved user instance.
        """
        user = User(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer.

    Extends SimpleJWT's `TokenObtainPairSerializer` by adding the `user_id`
    claim to the generated token. This allows downstream services, such as
    the Gateway and LLM service, to identify the authenticated user directly
    from the JWT without querying Django.
    """

    @classmethod
    def get_token(cls, user):
        """
        Generates a JWT containing the user's ID as a custom claim.

        Args:
            user: The authenticated user.

        Returns:
            Token: A JWT with the `user_id` claim included.
        """
        token = super().get_token(user)
        token["user_id"] = user.id
        return token