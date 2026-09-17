import { Modal } from 'bootstrap';
import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { Chat } from '../../../models/chat-model';

@Component({
  selector: 'app-chat-delete-modal-component',
  standalone: true,
  imports: [],
  templateUrl: './chat-delete-modal-component.html',
  styleUrl: './chat-delete-modal-component.scss',
})
export class ChatDeleteModalComponent {
  @Input() selectedChat: Chat | null = null;
  @Output() confirmed = new EventEmitter<void>();
  showDeleteModal = false;

  constructor() {
  
  }

  open() {
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
