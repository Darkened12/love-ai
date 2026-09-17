import { Component, Input } from '@angular/core';
import { Message } from '../../../../models/message-model';
import { MarkdownModule } from 'ngx-markdown';
import { ChatService } from '../../../../services/chat-service';
import { Observable } from 'rxjs';
import { AsyncPipe } from '@angular/common';
import { UserProfile } from '../../../../models/user-profile-model';

@Component({
  selector: 'app-assistant-message-component',
  standalone: true,
  imports: [MarkdownModule, AsyncPipe],
  templateUrl: './assistant-message-component.html',
  styleUrl: './assistant-message-component.scss',
})
export class AssistantMessageComponent {
  @Input() message!: Message;
  @Input() chatId!: string | null;
  @Input() isLast: Boolean = false;
  @Input() userProfile!: UserProfile

  isStreaming$: Observable<boolean>;

  constructor(private chatService: ChatService) {
    this.isStreaming$ = this.chatService.isStreaming$
  }

  onRefresh() {
    if (!this.chatId) {
      return
    }
    this.chatService.refreshLastMessage(this.userProfile?.id, this.chatId, this.userProfile?.system_prompt);
  }
}
