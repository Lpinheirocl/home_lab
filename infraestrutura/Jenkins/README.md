# Jenkis ![alt text](image.png)
## O que é?
Jenkins é um servidor de automação de código aberto usado principalmente para integração contínua (CI) e entrega contínua (CD) no desenvolvimento de software. Ele automatiza tarefas como compilação, teste e implantação de código, facilitando a integração e entrega rápidas e eficientes de software. 
## Instalação e configuração: 
Tenha o Helm instalado 

Primeiro pegamos o a imagem do jenkis official
```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
```
Depois criamos uma Namespace para ter uma divisão logica e isolar os recursos
```bash
kubectl create namespace jenkins
```
Depois criamos um arquivo values.yaml para que possamos passar as configurações do jenkins
```bash
controller:
  admin:
    username: admin
    password: admin123

  serviceType: NodePort
  servicePort: 8080
  nodePort: 30080

  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1"
      memory: "1Gi"
```
Apos isso isntalamos o jenkins usando o arquivo values como parametros
```bash
helm install jenkins jenkins/jenkins -n jenkins -f values.yaml
```

