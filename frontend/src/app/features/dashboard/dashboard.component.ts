import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { catchError, map, of, startWith } from 'rxjs';
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

  readonly clusterStatus$ = this.dashboardApi.getHealth().pipe(
    map((): ClusterStatus => ({ label: 'API conectada', connected: true })),
    startWith({ label: 'Verificando API...', connected: false }),
    catchError(() => of({ label: 'API indisponível', connected: false })),
  );
}
