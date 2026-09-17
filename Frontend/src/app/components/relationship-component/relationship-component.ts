import { Component } from '@angular/core';
import { NavbarComponent } from '../navbar-component/navbar-component';
import { BehaviorSubject } from 'rxjs';
import { UserProfile } from '../../models/user-profile-model';
import { UserService } from '../../services/user-service';
import { RelationshipService } from '../../services/relationship-service';

@Component({
  selector: 'app-relationship-component',
  imports: [NavbarComponent],
  templateUrl: './relationship-component.html',
  styleUrl: './relationship-component.scss',
})
export class RelationshipComponent {
  userSubject = new BehaviorSubject<UserProfile | null>(null);
  user$ = this.userSubject.asObservable()

  constructor(private userService: UserService, private relationService: RelationshipService) {}

  ngOnInit() {
    this.userService.loadUser().subscribe(
      user => this.userSubject.next(user)
    );  
  }

  onResetPress() {
    const user = this.userSubject.value
    if (!user) return;

    this.relationService.resetRelationship(user.id).subscribe()
  }
}
