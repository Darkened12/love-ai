import { Component, effect, input } from '@angular/core';
import { UserProfile } from '../../../models/user-profile-model';
import { UserService } from '../../../services/user-service';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-system-prompt-component',
  imports: [FormsModule, AsyncPipe],
  templateUrl: './system-prompt-component.html',
  styleUrl: './system-prompt-component.scss',
})
export class SystemPromptComponent {
  userProfile = input<UserProfile | null>(null);
  saveSuccess = new Subject<boolean>();
  saveSuccess$ = this.saveSuccess.asObservable();

  systemPrompt = '';

  constructor(private userService: UserService) {
    effect(() => {
      const user = this.userProfile();

      if (user) {
        this.systemPrompt = user.system_prompt ?? '';
      }
    });
  }

  savePrompt() {
    this.saveSuccess.next(false)
    this.userService.patchSystemPrompt(this.systemPrompt).subscribe(
      value => this.saveSuccess.next(true)
    );
  }
}
