# RBAC do Home Server Manager

Os manifestos em `deployment/rbac/` concedem ao backend leitura para descoberta e monitoramento, além de `patch` restrito a Deployments para reiniciar e escalar aplicações:

- Namespaces.
- Pods e logs.
- Services.
- Events.
- Deployments.
- Ingresses.
- Métricas de Pods pela API `metrics.k8s.io`.

O backend não pode criar ou remover recursos e não tem acesso a Secrets. O patch de Deployment é usado somente pelos endpoints validados de reinício e escala.

Aplicação dos manifestos:

```bash
kubectl apply -f deployment/namespace.yaml
kubectl apply -f deployment/rbac/
```
