import { AsyncPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { catchError, combineLatest, map, of, shareReplay, startWith, switchMap, timer } from 'rxjs';
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
  imports: [AsyncPipe, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent {
  private readonly dashboardApi = inject(DashboardApiService);
  private readonly applicationsApi = inject(ApplicationsApiService);

  private readonly discovered$ = this.applicationsApi.discover().pipe(
    catchError(() => of([])),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  readonly applications$ = combineLatest([
    this.applicationsApi.list().pipe(catchError(() => of([] as Application[]))),
    this.discovered$,
  ]).pipe(
    map(([applications, discovered]) => applications.map((application) => {
      const candidate = discovered.find((item) => item.name === application.name && item.namespace === application.namespace);
      return application.access_url || !candidate?.access_url
        ? application
        : { ...application, access_url: candidate.access_url };
    })),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  readonly applicationsCount$ = this.applications$.pipe(
    map((applications) => applications.length),
    startWith(0),
  );

  readonly podsCount$ = this.discovered$.pipe(
    map((applications) => applications.reduce((total, application) => total + application.ready_replicas, 0)),
    startWith(0),
    catchError(() => of(0)),
  );

  readonly clusterStatus$ = this.dashboardApi.getHealth().pipe(
    map((): ClusterStatus => ({ label: 'API conectada', connected: true })),
    startWith({ label: 'Verificando API...', connected: false }),
    catchError(() => of({ label: 'API indisponível', connected: false })),
  );

  readonly telemetry$ = timer(0, 300000).pipe(
    switchMap(() => this.dashboardApi.getTelemetry().pipe(catchError(() => of(null)))),
    startWith(null),
    shareReplay({ bufferSize: 1, refCount: true }),
  );
}
