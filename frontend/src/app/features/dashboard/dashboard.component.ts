import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { catchError, map, of, shareReplay, startWith } from 'rxjs';
import { Application } from '../../core/models/application.model';
import { ApplicationsApiService } from '../../core/services/applications-api.service';
import { DashboardApiService } from '../../core/services/dashboard-api.service';

interface ClusterStatus {
  label: string;
  connected: boolean;
}

@Component({
  standalone: true,
  selector: 'hsm-dashboard',
  imports: [AsyncPipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent {
  private readonly dashboardApi = inject(DashboardApiService);
  private readonly applicationsApi = inject(ApplicationsApiService);

  readonly applications$ = this.applicationsApi.list().pipe(
    catchError(() => of([] as Application[])),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  readonly applicationsCount$ = this.applications$.pipe(
    map((applications) => applications.length),
    startWith(0),
  );

  readonly podsCount$ = this.applicationsApi.discover().pipe(
    map((applications) => applications.reduce((total, application) => total + application.ready_replicas, 0)),
    startWith(0),
    catchError(() => of(0)),
  );

  readonly clusterStatus$ = this.dashboardApi.getHealth().pipe(
    map((): ClusterStatus => ({ label: 'API conectada', connected: true })),
    startWith({ label: 'Verificando API...', connected: false }),
    catchError(() => of({ label: 'API indisponível', connected: false })),
  );
}
