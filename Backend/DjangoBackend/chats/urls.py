from django.urls import path
from chats.views import ChatCreationView, ChatListView, ChatTitleCreationView, ChatDateUpdate, ChatDeleteView, \
    CheckChatOwnership, ChatRenameView

urlpatterns = [
    path("create_chat/", ChatCreationView.as_view()),
    path("get_chats_list/", ChatListView.as_view()),
    path("create_chat_title/", ChatTitleCreationView.as_view()),
    path("update_chat_date/", ChatDateUpdate.as_view()),
    path("rename_chat_title/", ChatRenameView.as_view()),
    path("delete_chat/", ChatDeleteView.as_view()),
    path("check_chat_ownership/", CheckChatOwnership.as_view())
]
