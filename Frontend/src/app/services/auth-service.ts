// auth-service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  catchError,
  finalize,
  map,
  Observable,
  of,
  shareReplay,
  switchMap,
  tap,
  throwError,
} from 'rxjs';
import { TokenRequest } from '../models/token-request-model';
import { LoginForm } from '../models/login-form-model';
import { Chat } from '../models/chat-model';
import { Router } from '@angular/router';
import { URLS } from '../config/api';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = localStorage.getItem('refresh_token');
  private refreshInFlight$: Observable<string | null> | null = null;
  baseURL = URLS.auth;

  constructor(private http: HttpClient, private router: Router) {}

  initAuth(): Observable<void> {
    return this.ensureAccessToken().pipe(map(() => void 0));
  }

  ensureAccessToken(): Observable<string | null> {
    if (this.accessToken) {
      return of(this.accessToken);
    }

    if (!this.refreshToken) {
      return of(null);
    }

    if (this.refreshInFlight$) {
      return this.refreshInFlight$;
    }

    this.refreshInFlight$ = this.http
      .post<TokenRequest>(`${this.baseURL}/token/refresh/`, {
        refresh: this.refreshToken,
      })
      .pipe(
        tap((res) => {
          this.accessToken = res.access;
        }),
        map((res) => res.access),
        catchError((err) => {
          this.logout();
          return of(null);
        }),
        finalize(() => {
          this.refreshInFlight$ = null;
        }),
        shareReplay(1)
      );

    return this.refreshInFlight$;
  }

  getAccessToken(): Observable<TokenRequest> {
    if (!this.refreshToken) {
      return throwError(() => new Error('No refresh token'));
    }

    return this.http.post<TokenRequest>(`${this.baseURL}/token/refresh/`, {
      refresh: this.refreshToken,
    }).pipe(
      tap((res) => {
        this.accessToken = res.access;
      })
    );
  }

  getAcessTokenValue(): string | null {
    return this.accessToken;
  }

  hasAccessToken(): boolean {
    return this.accessToken !== null;
  }

  hasRefreshToken(): boolean {
    return this.refreshToken !== null;
  }

  setAccessToken(token: string) {
    this.accessToken = token;
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('refresh_token');
    this.router.navigate(['/login']);
  }

  auth(user: LoginForm): Observable<TokenRequest> {
    return this.http.post<TokenRequest>(`${this.baseURL}/token/`, {
      username: user.username,
      password: user.password,
    }).pipe(
      tap((res) => {
        this.accessToken = res.access;
        if (res.refresh) {
          this.refreshToken = res.refresh;
          localStorage.setItem('refresh_token', res.refresh);
        }
      })
    );
  }
}