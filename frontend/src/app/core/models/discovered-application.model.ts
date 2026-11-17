export interface DiscoveredApplication {
  name: string;
  namespace: string;
  display_name: string;
  deployment_name: string;
  replicas: number;
  ready_replicas: number;
  services: string[];
  ingress_hosts: string[];
  source: string;
}
