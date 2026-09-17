import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Chat } from '../../../models/chat-model';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat-rename-modal-component',
  imports: [FormsModule],
  templateUrl: './chat-rename-modal-component.html',
  styleUrl: './chat-rename-modal-component.scss',
})
export class ChatRenameModalComponent {
  @Input() selectedChat: Chat | null = null;
  @Output() confirmed = new EventEmitter<void>();

  showDeleteModal = false;
  renameTitleInput = '';

  constructor() {
  
  }

  open(chat: Chat) {
    this.renameTitleInput = chat.title
    this.showDeleteModal = true;
  }

  close() {
    this.showDeleteModal = false;
  }

  confirm() {
    this.confirmed.emit();
    this.close();
  }
}
