import { Component } from '@angular/core';
import { NavbarComponent } from '../navbar-component/navbar-component';
import { ProfilePicComponent } from './profile-pic-component/profile-pic-component';
import { UserService } from '../../services/user-service';
import { UserProfile } from '../../models/user-profile-model';
import { BehaviorSubject } from 'rxjs';
import { AsyncPipe } from '@angular/common';
import { ProfilePictureRequest } from '../../models/profile-picture-request-model';
import { SystemPromptComponent } from './system-prompt-component/system-prompt-component';

@Component({
  selector: 'app-settings-component',
  standalone: true,
  imports: [NavbarComponent, ProfilePicComponent, SystemPromptComponent, AsyncPipe],
  templateUrl: './settings-component.html',
  styleUrl: './settings-component.scss',
})
export class SettingsComponent {
  userProfileSubject = new BehaviorSubject<UserProfile | null>(null);
  userProfile$ = this.userProfileSubject.asObservable()

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.userService.loadUser().subscribe(
      (user: UserProfile) => { this.userProfileSubject.next(user) }
    )
  }

  onProfilePictureUpdated(response: ProfilePictureRequest) {
    const current = this.userProfileSubject.value;

    if (!current) return;

    this.userProfileSubject.next({
      ...current,
      profile_picture: response.profile_picture,
      assistant_profile_picture: response.assistant_profile_picture
    });
  }

}
