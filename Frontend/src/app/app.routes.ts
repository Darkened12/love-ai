import { Routes } from '@angular/router';
import { AuthComponent } from './components/login_page/auth-component/auth-component';
import { authGuard } from './guards/auth.guard';
import { ChatShellComponent } from './components/chat-shell-component/chat-shell-component';
import { loginGuard } from './guards/login.guard';
import { SettingsComponent } from './components/settings-component/settings-component';
import { MemoryComponent } from './components/memory_component/memory-component';


export const routes: Routes = [
    { path: 'login', component: AuthComponent, canActivate: [loginGuard]},
    { path: 'app', component: ChatShellComponent, canActivate: [authGuard]},
    { path: 'memory', component: MemoryComponent, canActivate: [authGuard]},
    { path: 'settings', component: SettingsComponent, canActivate: [authGuard]},
    { path: '', redirectTo: 'login', pathMatch: 'full' }
];
