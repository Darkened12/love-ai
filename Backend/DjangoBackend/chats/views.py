from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Chat


class ChatCreationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat = Chat.objects.create(
            user=request.user,
            title=request.data.get("title", "New Chat")
        )

        return Response({
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at,
            "last_updated_at": chat.last_updated_at,
        }, status=status.HTTP_201_CREATED)


class ChatTitleCreationView(APIView):
    def patch(self, request):
        chat_id = request.data.get("chat_id")
        title = request.data.get("title")

        chat = get_object_or_404(Chat, id=chat_id)

        chat.title = title
        chat.save()
        return Response(status=200)


class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chats = (
            request.user.chats
            .order_by("-last_updated_at")
            .values("id", "title", "created_at", "last_updated_at")
        )

        return Response(list(chats))


class ChatRenameView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        chat_id = request.data.get("chat_id")
        title = request.data.get("title")

        if not chat_id:
            return Response({"error": "chat_id is required"}, status=400)

        chat = request.user.chats.filter(id=chat_id).first()

        if not chat:
            return Response({"error": "Chat not found"}, status=404)

        chat.title = title
        chat.save()

        return Response(status=204)


class ChatDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        chat_id = request.query_params.get("chat_id")

        if not chat_id:
            return Response({"error": "chat_id is required"}, status=400)

        chat = request.user.chats.filter(id=chat_id).first()

        if not chat:
            return Response({"error": "Chat not found"}, status=404)

        chat.delete()
        return Response(status=204)


class ChatDateUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        chat_id = request.query_params.get("chat_id")

        if not chat_id:
            return Response({"error": "chat_id is required"}, status=400)

        chat = request.user.chats.filter(id=chat_id).first()

        if not chat:
            return Response({"error": "Chat not found"}, status=404)

        chat.last_updated_at = timezone.now()
        chat.save(update_fields=["last_updated_at"])

        return Response(status=204)


class CheckChatOwnership(APIView):
    def get(self, request):
        chat_id = request.query_params.get("chat_id")
        user_id = request.query_params.get("user_id")

        if not chat_id:
            return Response({"error": "chat_id is required"}, status=400)
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        chat_exists = Chat.objects.filter(
            id=chat_id,
            user_id=user_id,
        ).exists()

        if chat_exists:
            return Response({"success": True}, status=200)

        return Response({"success": False}, status=404)
