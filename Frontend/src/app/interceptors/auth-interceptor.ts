// auth-interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth-service';
import { catchError, switchMap, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  const isAuthRequest =
    req.url.endsWith('/auth/token/') ||
    req.url.endsWith('/auth/token/refresh/');

  if (isAuthRequest) {
    return next(req);
  }

  return auth.ensureAccessToken().pipe(
    switchMap((token) => {
      const authReq = token
        ? req.clone({
            setHeaders: {
              Authorization: `Bearer ${token}`,
            },
          })
        : req;

      const isRetry = req.headers.has('X-Retry');

      return next(authReq).pipe(
        catchError((error) => {
          if (error.status === 401 && !isRetry) {
            return auth.ensureAccessToken().pipe(
              switchMap((freshToken) => {
                if (!freshToken) {
                  auth.logout();
                  return throwError(() => error);
                }

                const retryReq = req.clone({
                  setHeaders: {
                    Authorization: `Bearer ${freshToken}`,
                    'X-Retry': 'true',
                  },
                });

                return next(retryReq);
              }),
              catchError(() => {
                auth.logout();
                return throwError(() => error);
              })
            );
          }

          return throwError(() => error);
        })
      );
    })
  );
};