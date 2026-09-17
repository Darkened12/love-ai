import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import Prism from 'prismjs';

(window as any).Prism = Prism;

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
