export interface DiskTelemetry {
  device: string;
  mountpoint: string;
  percent: number;
  used_bytes: number;
  total_bytes: number;
}

export interface Telemetry {
  cpu_percent: number;
  memory_percent: number;
  memory_used_bytes: number;
  memory_total_bytes: number;
  disks: DiskTelemetry[];
  network_received_bytes: number;
  network_transmitted_bytes: number;
  temperature_celsius: number | null;
}

