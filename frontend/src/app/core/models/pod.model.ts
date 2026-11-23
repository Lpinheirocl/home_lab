export interface Pod {
  name: string;
  namespace: string;
  status: string;
  ready: number;
  total: number;
  restarts: number;
  node: string | null;
  created_at: string | null;
  reason: string | null;
  restartable: boolean;
}

