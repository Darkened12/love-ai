import { Injectable } from '@angular/core';
import { AuthService } from './auth-service';
import { switchMap } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { URLS } from '../config/api';

@Injectable({
  providedIn: 'root',
})
export class RelationshipService {
  constructor(private auth: AuthService, private http: HttpClient) {}

  resetRelationship(userId: number) {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        return this.http.delete<void>(`${URLS.llm}/reset_relationship`, {
          params: {
            user_id: userId
          }
        })
      })
    )
  }
}
