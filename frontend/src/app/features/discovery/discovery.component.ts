import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { ApplicationsApiService } from '../../core/services/applications-api.service';
import { DiscoveredApplication } from '../../core/models/discovered-application.model';

@Component({
  standalone: true,
  selector: 'hsm-discovery',
  templateUrl: './discovery.component.html',
  styleUrl: './discovery.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DiscoveryComponent {
  private readonly api = inject(ApplicationsApiService);
  readonly candidates = signal<DiscoveredApplication[]>([]);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly saving = signal<string | null>(null);

  constructor() {
    this.discover();
  }

  discover(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.discover().subscribe({
      next: (candidates) => { this.candidates.set(candidates); this.loading.set(false); },
      error: (response: { error?: { detail?: string } }) => {
        this.error.set(response.error?.detail ?? 'Não foi possível consultar o Kubernetes.');
        this.loading.set(false);
      },
    });
  }

  confirm(candidate: DiscoveredApplication): void {
    this.saving.set(candidate.name);
    this.api.create({
      name: candidate.name,
      display_name: candidate.display_name,
      namespace: candidate.namespace,
      access_url: candidate.ingress_hosts[0] ? `https://${candidate.ingress_hosts[0]}` : undefined,
      favorite: false,
      visible: true,
    }).subscribe({
      next: () => { this.candidates.update((items) => items.filter((item) => item.name !== candidate.name || item.namespace !== candidate.namespace)); this.saving.set(null); },
      error: (response: { error?: { detail?: string } }) => { this.error.set(response.error?.detail ?? 'Não foi possível confirmar a aplicação.'); this.saving.set(null); },
    });
  }
}
