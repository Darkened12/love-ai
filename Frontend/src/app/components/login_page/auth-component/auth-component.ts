import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth-service';
import { Router } from '@angular/router';
import { TokenRequest } from '../../../models/token-request-model';

@Component({
  selector: 'app-auth-component',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './auth-component.html',
  styleUrl: './auth-component.scss',
})
export class AuthComponent {
  loginForm!: FormGroup;
  
  constructor(private fb: FormBuilder,
              private auth: AuthService,
              private router: Router) {}

  ngOnInit() {
    if (this.auth.hasAccessToken()) this.router.navigate(['/app']);

    this.loginForm = this.fb.group({
      username: ['', [
        Validators.required, 
        Validators.minLength(6),
        Validators.pattern(/^[a-zA-Z0-9_]+$/)
      ]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  getErrorMessages(controlName: string): string[] {
    const control = this.loginForm.get(controlName);
    if (!control || !control.errors || !control.touched) return [];
    
    const errors = control.errors;
    const messages: string[] = [];
    
    if (errors['required']) messages.push('This field is required.');
    if (errors['minlength']) messages.push(`Minimum length is ${errors['minlength'].requiredLength} characters.`);
    if (errors['maxlength']) messages.push(`Maximum length is ${errors['maxlength'].requiredLength} characters.`);
    if (errors['pattern']) messages.push('Invalid format.');

    return messages;
  }

  onSubmit() {
    if (this.loginForm.valid) {
      this.auth.auth(this.loginForm.value).subscribe(
        (token: TokenRequest) => {
          if (this.auth.hasAccessToken()) {
            this.router.navigate(['/app']);
          }
        }
      )

    }
  }
}
