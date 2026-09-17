import { Component, effect, EventEmitter, input, Output, output } from '@angular/core';
import { Chat } from '../../../models/chat-model';
import { ChatService } from '../../../services/chat-service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat-list-component',
  imports: [FormsModule],
  templateUrl: './chat-list-component.html',
  styleUrl: './chat-list-component.scss',
})
export class ChatListComponent {
  chatsList = input<Chat[]>();
  chatId = input<string>();
  updatedChatsList = output<Chat[]>();

  @Output() deleteRequested = new EventEmitter<Chat>();
  @Output() renameRequested = new EventEmitter<Chat>();

  constructor(private chatService: ChatService) {
    effect(() => {
      const chatId = this.chatId;

    })
  }

  openRenameModal(chat: Chat) {
    this.renameRequested.emit(chat);
  }

  openDeleteModal(chat: Chat) {
    this.deleteRequested.emit(chat);
  }
  
  onChatClick(chat: Chat) {
    const chatslist = this.chatsList();
    if (!chatslist) return;
    const filteredChatslist = chatslist.filter(c => c.id !== chat.id);
    this.updatedChatsList.emit([chat, ...filteredChatslist]);
  }

  onCreateButtonPress() {
    const chatsList = this.chatsList();
    if (!chatsList) return;
    this.chatService.createChat().subscribe(
      (chat: Chat) => this.updatedChatsList.emit([chat, ...chatsList])
    )
  }
}
