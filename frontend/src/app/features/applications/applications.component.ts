import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Application } from '../../core/models/application.model';
import { ApplicationsApiService } from '../../core/services/applications-api.service';

@Component({
  standalone: true,
  selector: 'hsm-applications',
  imports: [ReactiveFormsModule],
  templateUrl: './applications.component.html',
  styleUrl: './applications.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ApplicationsComponent {
  private readonly api = inject(ApplicationsApiService);
  private readonly formBuilder = inject(FormBuilder);
  readonly applications = signal<Application[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly form = this.formBuilder.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(120)]],
    display_name: ['', [Validators.required, Validators.maxLength(120)]],
    description: [''], category: [''], namespace: [''], access_url: [''], favorite: [false], visible: [true],
  });

  constructor() { this.loadApplications(); }

  loadApplications(): void {
    this.loading.set(true);
    this.api.list().subscribe({
      next: (applications) => { this.applications.set(applications); this.loading.set(false); },
      error: () => { this.error.set('Não foi possível carregar as aplicações.'); this.loading.set(false); },
    });
  }

  createApplication(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.saving.set(true);
    this.error.set(null);
    this.api.create(this.form.getRawValue()).subscribe({
      next: () => { this.form.reset({ favorite: false, visible: true }); this.saving.set(false); this.loadApplications(); },
      error: (response: { error?: { detail?: string } }) => { this.error.set(response.error?.detail ?? 'Não foi possível cadastrar a aplicação.'); this.saving.set(false); },
    });
  }

  deleteApplication(application: Application): void {
    if (!confirm(`Remover o cadastro de ${application.display_name}?`)) return;
    this.api.delete(application.id).subscribe({ next: () => this.loadApplications(), error: () => this.error.set('Não foi possível remover a aplicação.') });
  }
}
