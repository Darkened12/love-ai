import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './auth-service';
import { Observable, switchMap, throwError } from 'rxjs';
import { Memory } from '../models/memory-models';
import { URLS } from '../config/api';

@Injectable({
  providedIn: 'root',
})
export class MemoryService {
  baseURL = URLS.llm;
  constructor(private http: HttpClient, private auth: AuthService) {}

  getMemoryList(): Observable<Memory[]> {
    return this.auth.ensureAccessToken().pipe(
          switchMap(token => {
            if (!token) {
              return throwError(() => new Error('No access token'));
            }
    
            return this.makeRequest(token);
          })
        );
  }

  private makeRequest(token: string): Observable<Memory[]> {
    return this.http.get<Memory[]>(`${this.baseURL}/fetch_user_facts`);
  }

  deleteMemory(memory: Memory) {
    return this.auth.ensureAccessToken().pipe(
          switchMap(token => {
            if (!token) {
              return throwError(() => new Error('No access token'));
            }
    
            return this.http.delete(`${this.baseURL}/delete_memory`, {
              params: {
                id: memory.id
              }
            });
          })
        );
  }
}
