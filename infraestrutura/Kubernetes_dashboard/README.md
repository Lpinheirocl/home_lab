# Dashboard Kubernetes
O dashboard serve para verificar nosso pods e quantas replicações, uma visão mas macro da infraestrutura.

## Configuraçao e instalação
Como utilizou o Raspeberry PI e sistema ARM, o dashboard do kubernetes atende o que precisamos para utilizar como dashboard.
Mas por uma melhor configuração instalamos uma versão mais otimizada.

instalando a imagem do dashboard
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

Criando a conta de acesso (Admin User)
```bash
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```
Aplicando a configuraçao
```bash
kubectl apply -f dashboard-admin.yaml
```
Alterando o ClusterIP para NodePort
```bash
kubectl -n kubernetes-dashboard edit service kubernetes-dashboard
```

Localiza :
```bash
type: ClusterIP
```
troca por:
```bash
type: NodePort
```

Apos alteração execute, para saber a porta do dashboard:
```bash
kubectl -n kubernetes-dashboard get svc kubernetes-dashboard
```
Apos acessar o dashboard utilizando o HTTPS, execute o comando a baixa para gerar o token para o acesso:
```bash
kubectl -n kubernetes-dashboard create token admin-user
```