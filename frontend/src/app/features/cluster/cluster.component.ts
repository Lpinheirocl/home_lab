import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { catchError, of, switchMap, timer } from 'rxjs';
import { DashboardApiService } from '../../core/services/dashboard-api.service';

@Component({
  standalone: true,
  selector: 'hsm-cluster',
  imports: [AsyncPipe],
  templateUrl: './cluster.component.html',
  styleUrl: './cluster.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClusterComponent {
  private readonly api = inject(DashboardApiService);
  readonly activeResource = signal<string | null>(null);
  toggleResource(resource: string): void {
    this.activeResource.update((active) => active === resource ? null : resource);
  }
  readonly namespaces$ = timer(0, 60000).pipe(switchMap(() => this.api.getNamespaces().pipe(catchError(() => of([])))));
  readonly deployments$ = timer(0, 60000).pipe(switchMap(() => this.api.getDeployments().pipe(catchError(() => of([])))));
  readonly services$ = timer(0, 60000).pipe(switchMap(() => this.api.getServices().pipe(catchError(() => of([])))));
  readonly ingresses$ = timer(0, 60000).pipe(switchMap(() => this.api.getIngresses().pipe(catchError(() => of([])))));
  readonly events$ = timer(0, 60000).pipe(switchMap(() => this.api.getEvents().pipe(catchError(() => of([])))));
  readonly metrics$ = timer(0, 60000).pipe(switchMap(() => this.api.getWorkloadMetrics().pipe(catchError(() => of(null)))));
}
