import { AsyncPipe, DatePipe, DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { catchError, combineLatest, map, of, shareReplay, startWith, switchMap, timer } from 'rxjs';
import { Application } from '../../core/models/application.model';
import { ApplicationsApiService } from '../../core/services/applications-api.service';
import { DashboardApiService, DashboardData } from '../../core/services/dashboard-api.service';
import { webSocket } from 'rxjs/webSocket';

@Component({
  standalone: true,
  selector: 'hsm-dashboard',
  imports: [AsyncPipe, DatePipe, DecimalPipe, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent {
  private readonly dashboardApi = inject(DashboardApiService);
  private readonly applicationsApi = inject(ApplicationsApiService);

  private readonly discovered$ = timer(0, 60000).pipe(
    switchMap(() => this.applicationsApi.discover().pipe(catchError(() => of([])))),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  readonly applications$ = timer(0, 60000).pipe(
    switchMap(() => combineLatest([
      this.applicationsApi.list().pipe(catchError(() => of([] as Application[]))), this.discovered$,
    ])),
    map(([applications, discovered]) => applications
      .filter((application) => application.visible)
      .map((application) => {
        const candidate = discovered.find((item) => item.name === application.name && item.namespace === application.namespace);
        return application.access_url || !candidate?.access_url
          ? application
          : { ...application, access_url: candidate.access_url };
      })
      .sort((a, b) => Number(b.favorite) - Number(a.favorite))),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  readonly dashboard$ = timer(0, 60000).pipe(
    switchMap(() => this.dashboardApi.getDashboard().pipe(
      map((data): {data: DashboardData | null; error: string | null; loading: boolean} => ({data, error: null, loading: false})),
      catchError((error) => of({
        data: null,
        error: error?.error?.detail ?? 'Não foi possível consultar o cluster. Verifique os logs da API.',
        loading: false,
      })),
    )),
    startWith({data: null, error: null, loading: true}),
    shareReplay({bufferSize: 1, refCount: true}),
  );

  readonly telemetry$ = timer(0, 300000).pipe(
    switchMap(() => this.dashboardApi.getTelemetry().pipe(catchError(() => of(null)))),
    startWith(null),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  readonly metricsHistory$ = timer(0, 300000).pipe(
    switchMap(() => this.dashboardApi.getMetricsHistory().pipe(catchError(() => of(null)))),
    shareReplay(1),
  );
  readonly live$ = webSocket<{
    type: string;
    pods_running?: number;
    pods_total?: number;
    telemetry?: {cpu_percent: number; memory_percent: number};
  }>(
    `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/dashboard`,
  ).pipe(catchError(() => of(null)), shareReplay(1));
}
