![alt text](image.png)
# O que é K3s?
O K3s é uma distribuição leve do Kubernetes desenvolvida pela Rancher Labs. Ele é projetado para ser simples de instalar e gerenciar, mantendo a compatibilidade com o Kubernetes original. Ele usa containerd como runtime de containers, mas também suporta Docker.

## Instalação do K3s
Instale o K3s:
Execute o seguinte comando no terminal
```bash
curl -sfL https://get.k3s.io | sh -
```

## Instale o K3s com o Docker como runtime
```bash
curl -sfL https://get.k3s.io | sh -s - --docker
```
## Instale o Docker
https://docs.docker.com/engine/install/.

## O K3s gera um arquivo de configuração do Kubernetes em /etc/rancher/k3s/k3s.yaml. Para usar o kubectl
```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

## Para não utilizar o modo administrador para os comandos do kubectl seguimos o passo a passo
```bash
sudo kubectl get nodes --kubeconfig /etc/rancher/k3s/k3s.yaml
```
## Cria a pasta .Kube
```bash
mkdir -p ~/.kube
```
## torna os comandos kubectl para o usuario
```bash
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
```



