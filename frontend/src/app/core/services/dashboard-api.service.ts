import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiHealth } from '../models/api-health.model';
import { Pod } from '../models/pod.model';
import { Telemetry } from '../models/telemetry.model';

export interface DashboardData {
  cluster_connected: boolean;
  applications_total: number;
  applications_online: number;
  applications_offline: number;
  pods_running: number;
  pods_total: number;
  applications: { id: number; name: string; display_name: string; namespace: string | null; status: string; ready_replicas: number; replicas: number }[];
  recent_events: { namespace: string; name: string; reason: string | null; message: string; event_type: string | null; created_at: string | null }[];
}

@Injectable({ providedIn: 'root' })
export class DashboardApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1';

  getHealth(): Observable<ApiHealth> {
    return this.http.get<ApiHealth>(`${this.apiUrl}/health`);
  }

  getPods(): Observable<Pod[]> { return this.http.get<Pod[]>(`${this.apiUrl}/pods`); }
  getTelemetry(): Observable<Telemetry> { return this.http.get<Telemetry>(`${this.apiUrl}/telemetry`); }
  getDashboard(): Observable<DashboardData> { return this.http.get<DashboardData>(`${this.apiUrl}/dashboard`); }
  getMetricsHistory(): Observable<{available: boolean; cpu_history: {timestamp: string; value: number}[]; memory_history: {timestamp: string; value: number}[]}> {
    return this.http.get<{available: boolean; cpu_history: {timestamp: string; value: number}[]; memory_history: {timestamp: string; value: number}[]}>(`${this.apiUrl}/monitoring/metrics`);
  }
  getWorkloadMetrics(): Observable<{namespace: string; pod: string; cpu: string; memory: string}[]> {
    return this.http.get<{namespace: string; pod: string; cpu: string; memory: string}[]>(`${this.apiUrl}/monitoring/workloads`);
  }
  getNamespaces(): Observable<{name: string; status: string}[]> { return this.http.get<{name: string; status: string}[]>(`${this.apiUrl}/namespaces`); }
  getDeployments(): Observable<{name: string; namespace: string; replicas: number; ready_replicas: number; available_replicas: number}[]> {
    return this.http.get<{name: string; namespace: string; replicas: number; ready_replicas: number; available_replicas: number}[]>(`${this.apiUrl}/kubernetes/deployments`);
  }
  getServices(): Observable<{name: string; namespace: string; type: string; cluster_ip: string | null; ports: string[]}[]> {
    return this.http.get<{name: string; namespace: string; type: string; cluster_ip: string | null; ports: string[]}[]>(`${this.apiUrl}/kubernetes/services`);
  }
  getIngresses(): Observable<{name: string; namespace: string; hosts: string[]; addresses: string[]}[]> {
    return this.http.get<{name: string; namespace: string; hosts: string[]; addresses: string[]}[]>(`${this.apiUrl}/kubernetes/ingresses`);
  }
  getEvents(): Observable<{namespace: string; name: string; reason: string | null; message: string; event_type: string | null; created_at: string | null}[]> {
    return this.http.get<{namespace: string; name: string; reason: string | null; message: string; event_type: string | null; created_at: string | null}[]>(`${this.apiUrl}/kubernetes/events`);
  }
}
