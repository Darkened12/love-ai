import { Component, input, effect  } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { ChatService } from '../../../services/chat-service';
import { Message } from '../../../models/message-model';
import { Observable } from 'rxjs';
import { UserMessageComponent } from './user-message-component/user-message-component';
import { AssistantMessageComponent } from './assistant-message-component/assistant-message-component';
import { UserProfile } from '../../../models/user-profile-model';
import { Chat } from '../../../models/chat-model';

@Component({
  selector: 'app-chat-component',
  standalone: true,
  imports: [AsyncPipe, UserMessageComponent, AssistantMessageComponent],
  templateUrl: './chat-component.html',
  styleUrl: './chat-component.scss',
})
export class ChatComponent {
  messages$: Observable<Message[]>;
  loading$: Observable<boolean>;
  chatId = input<string | null>(null);
  chatsList = input<Chat[]>();
  userProfile = input<UserProfile | null>(null);

  constructor(private chatService: ChatService) {
    this.messages$ = this.chatService.messages$;
    this.loading$ = this.chatService.loading$;

    effect(() => {
      const chatId = this.chatId();

      if (!chatId) return;

      this.chatService.loadMessages(chatId);
    })
  }

  onCreateButtonPress() {
    const chatsList = this.chatsList();
    if (!chatsList) return;
    this.chatService.createChat().subscribe(
      (chat: Chat) => this.chatService.onUpdateChatList([chat, ...chatsList])
    )
  }

}