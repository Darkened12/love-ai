from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from config import GATEWAY_URL

from users.models import User


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "system_prompt": user.system_prompt,
            "profile_picture": GATEWAY_URL + user.profile_picture.url
            if user.profile_picture else None,
            "assistant_profile_picture": GATEWAY_URL + user.assistant_profile_picture.url
            if user.assistant_profile_picture else None,
        })

    def patch(self, request):
        user = request.user

        if "system_prompt" not in request.data:
            return Response({"error": '"system_prompt" is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user.system_prompt = request.data["system_prompt"]
        user.save()

        return Response({"success": True})

    def post(self, request):
        user = request.user

        if not any(key in request.FILES for key in ("profile_picture", "assistant_profile_picture")):
            return Response(
                {"error": "No image was sent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "profile_picture" in request.FILES:
            if user.profile_picture:
                user.profile_picture.delete(save=False)

            user.profile_picture = request.FILES["profile_picture"]

        if "assistant_profile_picture" in request.FILES:
            if user.assistant_profile_picture:
                user.assistant_profile_picture.delete(save=False)

            user.assistant_profile_picture = request.FILES["assistant_profile_picture"]

        user.save()

        return Response({
            "success": True,
            "profile_picture": GATEWAY_URL + user.profile_picture.url if user.profile_picture else None,
            "assistant_profile_picture": (
                GATEWAY_URL + user.assistant_profile_picture.url
                if user.assistant_profile_picture else None
            ),
        })


class UserLastMessageAtView(APIView):
    def get(self, request):
        users = User.objects.filter(last_message_at__isnull=False)

        return Response([
            {
                "id": user.id,
                "last_message_at": user.last_message_at
            }
            for user in users
        ])