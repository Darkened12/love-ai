import { Injectable } from '@angular/core';
import { AuthService } from './auth-service';
import { switchMap, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { URLS } from '../config/api';
import { RelationshipModel } from '../models/relationship-model';

@Injectable({
  providedIn: 'root',
})
export class RelationshipService {
  constructor(private auth: AuthService, private http: HttpClient) {}

  getRelationship(userId: number): Observable<RelationshipModel> {
    return this.auth.ensureAccessToken().pipe(
      switchMap(token => {
        return this.http.get<RelationshipModel>(`${URLS.llm}/get_relationship`, {
          params: {
            user_id: userId
          }
        })
      })
    )
  }
  
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
