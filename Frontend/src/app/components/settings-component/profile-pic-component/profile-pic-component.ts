import { Component, input, output } from '@angular/core';
import { UserService } from '../../../services/user-service';
import { UserProfile } from '../../../models/user-profile-model';
import { ProfilePictureRequest } from '../../../models/profile-picture-request-model';
import { BehaviorSubject } from 'rxjs';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-profile-pic-component',
  imports: [AsyncPipe],
  templateUrl: './profile-pic-component.html',
  styleUrl: './profile-pic-component.scss',
})
export class ProfilePicComponent {
    userProfile = input<UserProfile | null>(null);
    updatedUserProfilePicture = output<ProfilePictureRequest>();
    updatedAssistantProfilePicture = output<ProfilePictureRequest>();
    uploadSuccess = new BehaviorSubject(false);
    uploadSuccess$ = this.uploadSuccess.asObservable();

    constructor(private userService: UserService) {}

    onUserProfilePictureSelected(event: Event) {
        this.uploadSuccess.next(false);
        const input = event.target as HTMLInputElement;

        if (!input.files?.length) {
            return;
        }

        const file = input.files[0];
        this.userService.postProfilePicture(file).subscribe(
            (response: ProfilePictureRequest) => { 
                this.updatedUserProfilePicture.emit(response);
                this.uploadSuccess.next(true);
             }
        )
    }

    onAssistantProfilePictureSelected(event: Event) {
        this.uploadSuccess.next(false);
        const input = event.target as HTMLInputElement;

        if (!input.files?.length) {
            return;
        }

        const file = input.files[0];
        this.userService.postProfilePicture(file, true).subscribe(
            (response: ProfilePictureRequest) => { 
                this.updatedAssistantProfilePicture.emit(response);
                this.uploadSuccess.next(true); 
            }
        )
    }


}
