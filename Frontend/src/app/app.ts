import { Component, signal, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth-service';
import { WebsocketsService } from './services/websockets-service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('love-ai');

  constructor(private auth: AuthService, private ws: WebsocketsService) {}
  
  ngOnInit() {
    this.auth.initAuth().subscribe();
    this.auth.ensureAccessToken().subscribe({
      next: token => { 
        if (!token) return;
        this.ws.connect(token) 
      },
      error: () => {} 
    })
  }
}
