import { Component, input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../../services/chat-service';
import { Message } from '../../../models/message-model';
import { AsyncPipe } from '@angular/common';
import { Observable, take } from 'rxjs';
import { UserProfile } from '../../../models/user-profile-model';

@Component({
  selector: 'app-input-component',
  standalone: true,
  imports: [FormsModule, AsyncPipe],
  templateUrl: './input-component.html',
  styleUrl: './input-component.scss',
})
export class InputComponent {
  message = '';
  messages: Message[] = []
  isStreaming$: Observable<boolean>;

  userProfile = input<UserProfile | null>(null);
  chatId = input<string | null>(null);

  constructor(private chatService: ChatService) {
    this.isStreaming$ = this.chatService.isStreaming$
    this.chatService.messages$.subscribe(
      (msg: Message[]) => {this.messages = msg}
    )
  }

  onEnter(event: KeyboardEvent) {
    event.preventDefault();

    if (!this.chatId()) {
      return
    }

    this.isStreaming$.pipe(take(1)).subscribe(isStreaming => {
      if (!isStreaming) {
        this.handleSend();
      }
    });
  } 

  handleSend(event?: Event) {
    event?.preventDefault();

    const chatId = this.chatId();
    const userProfile = this.userProfile();

    if (!this.message.trim()  || !chatId) return;
    if (!userProfile) return;

    this.chatService.sendMessage(userProfile?.id, chatId, this.message, userProfile?.system_prompt);
    this.message = '';
  }
}
