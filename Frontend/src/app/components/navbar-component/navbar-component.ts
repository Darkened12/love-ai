import { Component, input } from '@angular/core';
import { AuthService } from '../../services/auth-service';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';
import { Chat } from '../../models/chat-model';
import { BehaviorSubject } from 'rxjs';
import { ChatService } from '../../services/chat-service';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-navbar-component',
  standalone: true,
  imports: [RouterLink, AsyncPipe],
  templateUrl: './navbar-component.html',
  styleUrl: './navbar-component.scss',
})
export class NavbarComponent {
  private currentChat = new BehaviorSubject<Chat | null>(null);
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

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
