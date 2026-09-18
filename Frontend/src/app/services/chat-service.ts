import { Injectable } from '@angular/core';
import { Message } from '../models/message-model';
import { BehaviorSubject, filter, Observable, switchMap, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth-service';
import { Chat } from '../models/chat-model';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { URLS } from '../config/api';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private chatsSubject = new BehaviorSubject<Chat[]>([]);
  chats$ = this.chatsSubject.asObservable();

  private currentChatSubject = new BehaviorSubject<Chat | null>(null);
  currentChat$ = this.currentChatSubject.asObservable();

  private chatId = new BehaviorSubject<string>('');
  chatId$ = this.chatId.asObservable();

  private messagesSubject = new BehaviorSubject<Message[]>([]);
  messages$ = this.messagesSubject.asObservable();

  private loadingSubject = new BehaviorSubject(false);
  loading$ = this.loadingSubject.asObservable();

  private isStreamingSubject = new BehaviorSubject(false);
  isStreaming$ = this.isStreamingSubject.asObservable();

  private llmURL = URLS.llm;
  private chatsURL = URLS.chats;

  constructor(private http: HttpClient, private auth: AuthService) {
    this.chats$.pipe(filter(chats => chats.length > 0), takeUntilDestroyed()).subscribe(
      (chatsList: Chat[]) => {
        this.chatId.next(chatsList[0].id);
      } 
    );

    this.chats$.pipe(filter(chats => chats.length > 0), takeUntilDestroyed()).subscribe(
      (chatsList: Chat[]) => {
        this.currentChatSubject.next(chatsList[0])
      }
    );
  }

  cleanUp () {
    this.chatsSubject.next([]);
    this.currentChatSubject.next(null);
    this.chatId.next('');
    this.messagesSubject.next([]);
  }

  doEmptyMessages() {
    this.messagesSubject.next([]);
  }

  doEmptyChatId() {
    this.chatId.next('');
  }

  onUpdateChatList(chats: Chat[]) {
    this.chatsSubject.next(chats);
  }

  onUpdateCurrentChat(chat: Chat) {
    this.currentChatSubject.next(chat); 
  }

  onUpdateChatId(chatId: string) {
    this.chatId.next(chatId);
  }

  loadChats(): Observable<Chat[]> {
    return this.auth.ensureAccessToken().pipe(
      switchMap(
          token => {
            if (!token) { return throwError(() => new Error('loadChat: No Acess Token'))};
            
            return this.http.get<Chat[]>(`${this.chatsURL}/get_chats_list/`, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            })
        }
      )
    )
    
  }

  loadMessages(chatId: string) {
  this.loadingSubject.next(true);

  this.getChatHistory(chatId).subscribe({
    next: (msgs) => {
      this.messagesSubject.next(msgs);
      this.loadingSubject.next(false);
      },
      error: () => {
        this.loadingSubject.next(false);
      }
    });
  }

  getChatHistory(chatId: string): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.chatsURL}/fetch_chat_history`, {
      params: {
        chat_id: chatId
      }
    });
  }

  createChat(): Observable<Chat> {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        if (!token) return throwError(() => new Error("createChat: No acess token"));
        
        return this.http.post<Chat>(`${this.chatsURL}/create_chat/`, {
          headers: {
              Authorization: `Bearer ${token}`,
          },
        })
      })
    )
  }

  updateLocalTitle(chatId: string, title: string) {
    const chatsNew = this.chatsSubject.value.map(chat =>
      chat.id === chatId
        ? { ...chat, title }
        : chat
    );

    this.chatsSubject.next(chatsNew);
  }

  updateBackendTitle(chatId: string, title: string) {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        return this.http.patch<void>(
          `${this.chatsURL}/rename_chat_title`,
          {
            title,
            chat_id: chatId,
          }, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
      })
    );
  }

  updateChatDate(chatId: string) {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        return this.http.patch<void>(
          `${this.chatsURL}/update_chat_date`,
          null,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            params: {
              chat_id: chatId
            }
          }
        );
      })
    );
  }

  deleteChat(chatId: string): Observable<void> {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        return this.http.delete<void>(`${this.chatsURL}/delete_chat`, {
          params: {
            chat_id: chatId
          },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      })
    )
    
  }
    
  sendMessage(userId: number, chatId: string, text: string, system_prompt: string | null = null) {
    const messagesLenght = this.messagesSubject.value.length;
    const userPosition = messagesLenght + 1
    const assistantPosition = messagesLenght + 2

    const userMessage: Message = {
      id: userPosition,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    const assistantMessage: Message = {
      id: assistantPosition,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };

    this.messagesSubject.next([
      ...this.messagesSubject.value,
      userMessage,
      assistantMessage,
    ]);

    this.streamChat(userId, chatId, text, false, system_prompt).subscribe({
      next: (chunk) => {
        if (chunk.startsWith('__TITLE__:')) {
          this.updateLocalTitle(chatId, chunk.slice(10));
          return;
  }
        const messages = this.messagesSubject.value;
        const last = messages[messages.length - 1];

        last.content += chunk;
        this.messagesSubject.next([...messages]);
      },
      complete: () => {
          this.updateChatDate(chatId).subscribe(() => {
            this.loadChats().subscribe();
        });
      }
    });
  }

  refreshLastMessage(userId: number, chatId: string, system_prompt: string | null = null) {
    const msgs = this.messagesSubject.value;

    if (msgs.length === 0) return;

    const updated = [...msgs];
    updated[updated.length - 1] = {
      ...updated[updated.length - 1],
      content: ''
    };

    this.messagesSubject.next(updated);

    const lastUserMessage = updated[updated.length - 2];
    if (lastUserMessage.role !== "user") {
      throw new Error("RefreshingMessageError: not a 'user' message");
    }

    this.streamChat(userId, chatId, lastUserMessage.content, true, system_prompt).subscribe({
      next: (chunk) => {
        const messages = this.messagesSubject.value;
        const last = messages[messages.length - 1];

        last.content += chunk;
        this.messagesSubject.next([...messages]);
      },
    });
  }

  streamChat(userId: number, 
            chatId: string, 
            message: string, 
            refresh: boolean = false, 
            system_prompt: string | null = null): Observable<string> {
    return new Observable<string>((observer) => {
      this.isStreamingSubject.next(true);

      this.auth.ensureAccessToken().subscribe({
        next: (token) => {
          if (!token) {
            observer.error('No token');
            this.isStreamingSubject.next(false);
            return;
          }

          const url = refresh
            ? `${this.llmURL}/regenerate_message`
            : `${this.llmURL}/fetch_message`;

          const body = refresh
            ? JSON.stringify({
                user_id: userId,
                chat_id: chatId,
                system_prompt: system_prompt,
              })
            : JSON.stringify({
                user_id: userId,
                chat_id: chatId,
                message,
                system_prompt: system_prompt,
              });

          const controller = new AbortController();

          fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`, // FIX
            },
            body,
            signal: controller.signal,
          })
          .then(response => {
            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
              this.isStreamingSubject.next(false);
              observer.error('No reader');
              return;
            }

            const read = (): any => {
              reader.read().then(({ done, value }) => {
                if (done) {
                  this.isStreamingSubject.next(false);
                  observer.complete();
                  return;
                }

                observer.next(decoder.decode(value, { stream: true }));
                read();
              }).catch(err => {
                this.isStreamingSubject.next(false);
                observer.error(err);
              });
            };

            read();
          })
          .catch(err => {
            this.isStreamingSubject.next(false);
            observer.error(err);
          });

          return () => {
            controller.abort();
            this.isStreamingSubject.next(false);
          };
        },
        error: (err) => {
          this.isStreamingSubject.next(false);
          observer.error(err);
        }
      });
    });
  }
}
