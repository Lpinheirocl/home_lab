# RBAC do Home Server Manager

Os manifestos em `deployment/rbac/` concedem ao backend somente leitura sobre os recursos necessários para descoberta e consulta:

- Namespaces.
- Pods e logs.
- Services.
- Events.
- Deployments.
- Ingresses.

Não há permissões `create`, `update`, `patch`, `delete` ou acesso a Secrets.

Aplicação futura, somente após revisão:

```bash
kubectl apply -f deployment/namespace.yaml
kubectl apply -f deployment/rbac/
```

Esses comandos ainda não devem ser executados no servidor atual.
