import { Component, ElementRef, ViewChild } from '@angular/core';
import { InputComponent } from './input_component/input-component';
import { NavbarComponent } from '../navbar-component/navbar-component';
import { ChatComponent } from './chat-component/chat-component';
import { UserProfile } from '../../models/user-profile-model';
import { BehaviorSubject, filter } from 'rxjs';
import { UserService } from '../../services/user-service';
import { AsyncPipe } from '@angular/common';
import { ChatListComponent } from './chat-list-component/chat-list-component';
import { AuthService } from '../../services/auth-service';
import { Chat } from '../../models/chat-model';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ChatService } from '../../services/chat-service';
import { ChatDeleteModalComponent } from './chat-delete-modal-component/chat-delete-modal-component';
import { ChatRenameModalComponent } from './chat-rename-modal-component/chat-rename-modal-component';

@Component({
  selector: 'app-chat-shell-component',
  standalone: true,
  imports: [
    NavbarComponent,
    ChatComponent,
    InputComponent,
    ChatListComponent,
    ChatRenameModalComponent,
    ChatDeleteModalComponent,
    AsyncPipe,
  ],
  templateUrl: './chat-shell-component.html',
  styleUrl: './chat-shell-component.scss',
})
export class ChatShellComponent {
  userProfile = new BehaviorSubject<UserProfile | null>(null);
  userProfile$ = this.userProfile.asObservable();
  chatsList = new BehaviorSubject<Chat[]>([]);
  chatsList$ = this.chatsList.asObservable();
  chatId = new BehaviorSubject<string>('');
  chatId$ = this.chatId.asObservable();


  @ViewChild('scrollContainer')
  scrollContainer!: ElementRef<HTMLDivElement>;
  showScrollButton: boolean = false;

  @ViewChild('deleteModal') deleteModal!: ChatDeleteModalComponent;
  @ViewChild('renameModal') renameModal!: ChatRenameModalComponent;
  selectedChat: Chat | null = null;

  constructor(
      private userService: UserService,
      private auth: AuthService,
      private chatService: ChatService
    ) {
    this.chatService.chatId$.pipe(takeUntilDestroyed()).subscribe(
      chatId => this.chatId.next(chatId)
    );

    this.chatService.chats$.pipe(takeUntilDestroyed()).subscribe(
      chats => this.chatsList.next(chats)
    );
  }

  openDeleteModal(chat: Chat) {
    this.selectedChat = chat;
    this.deleteModal.open();
  }

   openRenameModal(chat: Chat) {
    this.selectedChat = chat;
    this.renameModal.open(chat);
  }

  onChatDelete() {
    const selectedChat = this.selectedChat
    if (!selectedChat) return;
    this.chatService.deleteChat(selectedChat.id).subscribe({
      next: () => {
        const chats = this.chatsList.value;
        if (!chats) return;

        const updatedChats = chats.filter(
          chat => chat.id !== selectedChat.id
        );
        this.chatService.onUpdateChatList(updatedChats);
        if (updatedChats.length === 0) {
          this.chatService.doEmptyMessages();
          this.chatService.doEmptyChatId();
        }
      },
    });
  }

  onRenameSubmit() {
    const chat = this.selectedChat
    const newTitle = this.renameModal.renameTitleInput

    if (!chat) return;
    this.chatService.updateBackendTitle(chat.id, newTitle).subscribe({
      next: () => {
        const updatedChats = this.chatsList.value.map(oldChat => {
          if (oldChat.id === chat.id) {
            oldChat.title = newTitle
            return oldChat
          }
          return oldChat
        });

        this.chatService.onUpdateChatList(updatedChats);
      }
    });
  }

  /**
 * Toggles the visibility of the "scroll to bottom" button based on the user's
 * current scroll position.
 *
 * Every time the scroll container moves, it calculates how many pixels remain
 * until the bottom of the conversation:
 *
 * distanceFromBottom = scrollHeight - scrollTop - clientHeight
 *
 * - scrollHeight: total height of the conversation.
 * - scrollTop: pixels already scrolled from the top.
 * - clientHeight: height of the visible area.
 *
 * The button is shown only when the user is more than 150 pixels away from
 * the bottom.
 */
  onScroll() {
    const el = this.scrollContainer.nativeElement;

    const distanceFromBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight;

    this.showScrollButton = distanceFromBottom > 150;
  }

  scrollToBottom() {
    const el = this.scrollContainer.nativeElement;

    el.scrollTo({
      top: el.scrollHeight,
      behavior: 'smooth'
    });

    this.showScrollButton = false;
  }

  updatedChatsList(chats: Chat[]) {
    this.chatService.onUpdateChatList(chats);
  }

  ngOnInit() {
    this.userService.loadUser().subscribe(
      (user: UserProfile) => { this.userProfile.next(user) }
    );

    this.chatService.loadChats().subscribe(
      (chats: Chat[]) => { 
        if (chats.length === 0) return;
        this.chatsList.next(chats);
        this.chatService.onUpdateChatId(chats[0].id);  // Loading the first chat
        this.chatService.onUpdateCurrentChat(chats[0]);
      }
    );
  }
}
