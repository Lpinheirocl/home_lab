import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { catchError, of, switchMap, timer } from 'rxjs';
import { DashboardApiService } from '../../core/services/dashboard-api.service';
import { signal } from '@angular/core';
import { Pod } from '../../core/models/pod.model';

@Component({
  standalone: true,
  selector: 'hsm-pods',
  imports: [AsyncPipe],
  templateUrl: './pods.component.html',
  styleUrl: './pods.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PodsComponent {
  private readonly api = inject(DashboardApiService);
  readonly pods$ = timer(0, 30000).pipe(switchMap(() => this.api.getPods().pipe(catchError(() => of([] as Pod[])))));
  readonly selectedLogs = signal<{pod: string; logs: string} | null>(null);
  readonly message = signal<string | null>(null);

  loadLogs(pod: Pod): void {
    this.message.set(null);
    this.api.getPodLogs(pod.namespace, pod.name).subscribe({
      next: (result) => this.selectedLogs.set(result),
      error: (error: {error?: {detail?: string}; status?: number}) =>
        this.message.set(error.error?.detail ?? `Falha ao consultar logs (HTTP ${error.status ?? 'sem resposta'}).`),
    });
  }

  restart(pod: Pod): void {
    if (!confirm(`Reiniciar o Deployment responsável por ${pod.name}?`)) return;
    this.api.restartPod(pod.namespace, pod.name).subscribe({
      next: (result) => this.message.set(result.message),
      error: (error: {error?: {detail?: string}; status?: number}) =>
        this.message.set(error.error?.detail ?? `Falha ao reiniciar (HTTP ${error.status ?? 'sem resposta'}).`),
    });
  }
}

