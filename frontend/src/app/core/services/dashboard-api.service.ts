import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiHealth } from '../models/api-health.model';

@Injectable({ providedIn: 'root' })
export class DashboardApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1';

  getHealth(): Observable<ApiHealth> {
    return this.http.get<ApiHealth>(`${this.apiUrl}/health`);
  }
}
