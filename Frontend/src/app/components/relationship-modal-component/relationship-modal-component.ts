import { Component, model } from '@angular/core';
import { BehaviorSubject, switchMap, tap } from 'rxjs';
import { UserProfile } from '../../models/user-profile-model';
import { UserService } from '../../services/user-service';
import { RelationshipService } from '../../services/relationship-service';
import { RelationshipModel } from '../../models/relationship-model';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-relationship-modal-component',
  imports: [AsyncPipe],
  templateUrl: './relationship-modal-component.html',
  styleUrl: './relationship-modal-component.scss',
})
export class RelationshipModalComponent {
  showRelationshipModal = model<boolean>(false);

  private userSubject = new BehaviorSubject<UserProfile | null>(null);
  user$ = this.userSubject.asObservable();

  private relationshipSubject = new BehaviorSubject<RelationshipModel | null>(null);
  relationship$ = this.relationshipSubject.asObservable();

  private resetSuccess = new BehaviorSubject(false);
  resetSuccess$ = this.resetSuccess.asObservable();

  constructor(private userService: UserService, private relationService: RelationshipService) {}

  ngOnInit() {
    this.userService.loadUser().pipe(
      tap(user => this.userSubject.next(user)),
      switchMap(user => this.relationService.getRelationship(user.id)),
      tap(relationship => this.relationshipSubject.next(relationship))
    ).subscribe();  
  }

  onResetPress() {
    const user = this.userSubject.value
    if (!user) return;

    this.resetSuccess.next(false);

    this.relationService.resetRelationship(user.id).pipe(
      switchMap(() => this.relationService.getRelationship(user.id)),
      tap(relationship => this.relationshipSubject.next(relationship)),
      tap(() => this.resetSuccess.next(true))
    ).subscribe();
  }

  onClose() {
    this.showRelationshipModal.set(false);
  }
}
