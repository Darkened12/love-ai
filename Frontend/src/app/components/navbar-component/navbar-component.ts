import { Component, input } from '@angular/core';
import { AuthService } from '../../services/auth-service';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';
import { Chat } from '../../models/chat-model';
import { BehaviorSubject } from 'rxjs';
import { ChatService } from '../../services/chat-service';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AsyncPipe } from '@angular/common';
import { RelationshipModalComponent } from '../relationship-modal-component/relationship-modal-component';

@Component({
  selector: 'app-navbar-component',
  standalone: true,
  imports: [RouterLink, AsyncPipe, RelationshipModalComponent],
  templateUrl: './navbar-component.html',
  styleUrl: './navbar-component.scss',
})
export class NavbarComponent {
  private currentChat = new BehaviorSubject<Chat | null>(null);
  showRelationshipModal = false;
  currentChat$ = this.currentChat.asObservable();

  constructor(private auth: AuthService,
              private router: Router,
              private chatService: ChatService
            ) {
    this.chatService.currentChat$.pipe(takeUntilDestroyed()).subscribe(
      chat => this.currentChat.next(chat)
    )
  }

  getCurrentRoute(): string {
    return this.router.url
  }

  onRelationshipPress() {
    this.showRelationshipModal = true;
  }

  logout() {
    this.auth.logout();
    this.chatService.cleanUp();
    this.router.navigate(['/login']);
  }
}
