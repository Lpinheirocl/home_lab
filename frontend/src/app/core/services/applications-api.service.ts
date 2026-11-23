import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Application, ApplicationCreate, ApplicationUpdate } from '../models/application.model';
import { DiscoveredApplication } from '../models/discovered-application.model';

@Injectable({ providedIn: 'root' })
export class ApplicationsApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1/applications';

  list(): Observable<Application[]> { return this.http.get<Application[]>(this.apiUrl); }
  create(payload: ApplicationCreate): Observable<Application> { return this.http.post<Application>(this.apiUrl, payload); }
  update(id: number, payload: ApplicationUpdate): Observable<Application> { return this.http.put<Application>(`${this.apiUrl}/${id}`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`${this.apiUrl}/${id}`); }
  discover(): Observable<DiscoveredApplication[]> { return this.http.post<DiscoveredApplication[]>(`${this.apiUrl}/discover`, {}); }
  logs(id: number): Observable<{application: string; logs: string}> { return this.http.get<{application: string; logs: string}>(`${this.apiUrl}/${id}/logs`); }
  restart(id: number): Observable<{status: string; message: string}> { return this.http.post<{status: string; message: string}>(`${this.apiUrl}/${id}/restart`, {}); }
  scale(id: number, replicas: number): Observable<{status: string; message: string}> {
    return this.http.post<{status: string; message: string}>(`${this.apiUrl}/${id}/scale`, {replicas});
  }
}
