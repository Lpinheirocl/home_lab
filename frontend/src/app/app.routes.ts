import { Routes } from '@angular/router';

export const routes: Routes = [
  {path: '', pathMatch: 'full', redirectTo: 'dashboard'},
  {path: 'dashboard', loadComponent: () => import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent)},
  {path: 'applications', loadComponent: () => import('./features/applications/applications.component').then((m) => m.ApplicationsComponent)},
  {path: 'pods', loadComponent: () => import('./features/pods/pods.component').then((m) => m.PodsComponent)},
  {path: 'cluster', loadComponent: () => import('./features/cluster/cluster.component').then((m) => m.ClusterComponent)},
  {path: 'discovery', loadComponent: () => import('./features/discovery/discovery.component').then((m) => m.DiscoveryComponent)},
  {path: '**', redirectTo: 'dashboard'},
];
