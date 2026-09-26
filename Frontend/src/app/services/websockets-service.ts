import { Injectable } from '@angular/core';
import { URLS } from '../config/api';
import { Subject } from 'rxjs';
import { WebsocketsMessage } from '../models/websockets-message-model';

@Injectable({
  providedIn: 'root',
})
export class WebsocketsService {
  private socket?: WebSocket;
  private messageSubject = new Subject<WebsocketsMessage>();
  message$ = this.messageSubject.asObservable();

  connect(token: string) {
    if (this.socket) {
      return;
    }

    this.socket = new WebSocket(
      `${URLS.ws}?token=${encodeURIComponent(token)}`
    );

    this.socket.onopen = () => {
      console.log("WebSocket connected");
    };

    this.socket.onmessage = event => {
      this.messageSubject.next(JSON.parse(event.data));
    };

    this.socket.onclose = () => {
      console.log("WebSocket closed");
      this.socket = undefined;
    };
  }

  disconnect() {
    this.socket?.close();
    this.socket = undefined;
  }
}
