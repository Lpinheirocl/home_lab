
# Home Server Manager

## Objetivo
Desenvolver uma plataforma de gerenciamento de servidor
inspirada no Umbrel.

## Infraestrutura existente
- Raspberry Pi 4 Model B
- Ubuntu Server
- K3s já instalado

## Tecnologias
- Frontend: Angular + TypeScript
- Backend: Python + FastAPI
- Banco: PostgreSQL
- Orquestração: K3s
- Integração: Kubernetes Python Client
- Comunicação: REST API + WebSocket

## Diretrizes
- Não substituir o K3s.
- Não utilizar Docker Compose como orquestrador principal.
- Descobrir aplicações já existentes no Kubernetes.
- Permitir cadastro manual de aplicações.
- Criar Dashboard com cards personalizáveis.
- Priorizar arquitetura modular.
- Garantir compatibilidade ARM64.
- Começar com operações somente leitura.
- Utilizar RBAC e permissões mínimas.
- Nunca executar comandos arbitrários recebidos do frontend.

## Documentação
Consultar PROJECT_SPEC.md antes de implementar funcionalidades.
