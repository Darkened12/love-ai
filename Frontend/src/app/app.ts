import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth-service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('love-ai');

  constructor(private auth: AuthService) {}
  
  ngOnInit() {
    this.auth.initAuth().subscribe();
  }
}
