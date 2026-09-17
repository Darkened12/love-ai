import { Component, Input } from '@angular/core';
import { Message } from '../../../../models/message-model';
import { UserProfile } from '../../../../models/user-profile-model';

@Component({
  selector: 'app-user-message-component',
  imports: [],
  templateUrl: './user-message-component.html',
  styleUrl: './user-message-component.scss',
})
export class UserMessageComponent {
  @Input() message!: Message;
  @Input() userProfile!: UserProfile;
}
