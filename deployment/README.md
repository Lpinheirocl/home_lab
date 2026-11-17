# Implantação no K3s

## Antes de aplicar

1. O workflow `.github/workflows/container-images.yml` publica as imagens no GHCR.
2. Configure os Secrets do GitHub Actions: `RPI_HOST`, `RPI_USER`, `RPI_SSH_PORT`, `RPI_SSH_PRIVATE_KEY`, `HSM_POSTGRES_PASSWORD` e `HSM_DATABASE_URL`.
3. Confirme que o Traefik está habilitado e que a StorageClass `local-path` existe.
4. Confirme que o SSD está sendo usado pelo provisionador de volumes do K3s.

## Construção das imagens ARM64

O build será executado automaticamente pelo GitHub Actions após um push nas branches configuradas. As imagens serão publicadas em:

```text
ghcr.io/lpinheirocl/home-server-manager-backend:arm64
ghcr.io/lpinheirocl/home-server-manager-frontend:arm64
```

Se os pacotes GHCR forem privados, será necessário criar um `imagePullSecret` no namespace e referenciá-lo nos Deployments. Para o primeiro teste, deixar os pacotes públicos simplifica o pull pelo Raspberry Pi.

## Aplicação no cluster

O workflow executará os comandos abaixo no Raspberry Pi:

```bash
kubectl apply -k deployment/
kubectl apply -f deployment/backend/migration-job.yaml
kubectl -n home-server-manager get pods,pvc,ingress
kubectl -n home-server-manager logs job/home-server-manager-migration
```

O Job de migração deve terminar com `Completed` antes de validar o backend.

## Acesso

O Ingress usa o host `home-server-manager.local`. Para teste local, crie uma entrada DNS ou em `/etc/hosts` apontando o IP do Raspberry Pi para esse nome.
