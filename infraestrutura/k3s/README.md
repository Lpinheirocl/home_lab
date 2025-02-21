![alt text](image.png)# O que é K3s?
O K3s é uma distribuição leve do Kubernetes desenvolvida pela Rancher Labs. Ele é projetado para ser simples de instalar e gerenciar, mantendo a compatibilidade com o Kubernetes original. Ele usa containerd como runtime de containers, mas também suporta Docker.

## Instalação do K3s
Instale o K3s:
Execute o seguinte comando no terminal
```bash
curl -sfL https://get.k3s.io | sh -
```

## O K3s gera um arquivo de configuração do Kubernetes em /etc/rancher/k3s/k3s.yaml. Para usar o kubectl
```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

## Instale o Docker
https://docs.docker.com/engine/install/.

## Instale o K3s com o Docker como runtime
```bash
curl -sfL https://get.k3s.io | sh -s - --docker
```

