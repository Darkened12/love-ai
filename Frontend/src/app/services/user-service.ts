import { Injectable } from '@angular/core';
import { AuthService } from './auth-service';
import { Observable, switchMap, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { UserProfile } from '../models/user-profile-model';
import { ProfilePictureRequest } from '../models/profile-picture-request-model';
import { URLS } from '../config/api';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private usersURL = URLS.users
  constructor(private auth: AuthService, private http: HttpClient) {}

  getUserProfile(token: string): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.usersURL}/profile/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  loadUser(): Observable<UserProfile> {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        if (!token) {
          return throwError(() => new Error('No access token'));
        }

        return this.getUserProfile(token);
      })
    );
  }

  patchSystemPrompt(systemPrompt: string) {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        if (!token) {
          return throwError(() => new Error('No access token'));
        }

        return this.http.patch(
          `${this.usersURL}/profile/`,
          { system_prompt: systemPrompt },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
      })
    );
  }

  postProfilePicture(file: File, assistant: boolean = false): Observable<ProfilePictureRequest> {
    const formData = new FormData();

    if (assistant) {
      formData.append('assistant_profile_picture', file);
    }
    else {
      formData.append('profile_picture', file);
    }

    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        if (!token) {
          return throwError(() => new Error('No access token'));
        }

        return this.http.post<ProfilePictureRequest>(
          `${this.usersURL}/profile/`,
          formData,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
      })
    );
  }
}
  
  

