# Arquitetura atual

O projeto usa Angular, FastAPI, PostgreSQL e K3s. A integração Kubernetes utiliza uma ServiceAccount com leitura dos recursos do cluster e permissão de patch somente em Deployments para reiniciar ou alterar réplicas por endpoints validados.

## Backend

- REST em `/api/v1` para catálogo, descoberta, Dashboard, namespaces, Pods, Deployments, Services, Ingresses, eventos, logs e métricas.
- WebSocket `/ws/dashboard`, com atualização de Pods e telemetria a cada 30 segundos.
- PostgreSQL para aplicações, recursos associados, eventos de operação, usuários e configurações.
- Prometheus e Node Exporter implantados no namespace `home-server-manager`; retenção local configurada para sete dias.
- Métricas de workloads consultadas pela API `metrics.k8s.io`, quando o Metrics Server está disponível no cluster.

## Frontend

- Dashboard de estado real do cluster e das aplicações, atividade recente e telemetria.
- Descoberta automática periódica, filtrando aplicações já cadastradas.
- Telas de aplicações, Pods e recursos do cluster.
- Consulta de logs e controles de reinício e escala para aplicações associadas a Deployments.

As operações administrativas usam somente a API oficial do Kubernetes. O backend não executa comandos de shell enviados pelo navegador.
