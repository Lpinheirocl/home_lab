import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { catchError, of, startWith } from 'rxjs';
import { DashboardApiService } from '../../core/services/dashboard-api.service';

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
  readonly pods$ = this.api.getPods().pipe(startWith(null), catchError(() => of([])));
}

