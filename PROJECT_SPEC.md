# 1. Visão geral do projeto

O Home Server Manager será uma plataforma web self-hosted destinada ao gerenciamento centralizado de um servidor doméstico baseado em Ubuntu Server e K3s.

A plataforma permitirá visualizar, descobrir, organizar, acessar e administrar aplicações existentes no cluster Kubernetes.

O sistema não terá como objetivo substituir o Kubernetes ou funcionar como uma loja pública de aplicações. Será uma camada de gerenciamento simplificada sobre a infraestrutura existente.

## 1.1 Objetivos principais

- Descobrir automaticamente aplicações instaladas no K3s.
- Criar um Dashboard visual com cards personalizáveis.
- Permitir acesso direto às aplicações.
- Monitorar o estado dos recursos Kubernetes.
- Gerenciar Deployments, Pods e Services.
- Consultar logs e eventos.
- Monitorar recursos do servidor.
- Organizar aplicações por categorias e namespaces.
- Permitir cadastro manual de aplicações externas ou não descobertas automaticamente.

# 2. Arquitetura tecnológica

| Camada | Tecnologia |
|---|---|
| Frontend | Angular |
| Linguagem frontend | TypeScript |
| Componentes visuais | Angular Material ou Tailwind CSS |
| Backend | Python |
| Framework API | FastAPI |
| ORM | SQLAlchemy |
| Banco de dados | PostgreSQL |
| Comunicação | REST API |
| Atualização em tempo real | WebSocket |
| Kubernetes | K3s |
| Integração Kubernetes | Kubernetes Python Client |
| Monitoramento | Prometheus |
| Gráficos | Chart.js |
| Proxy reverso | Traefik |
| Infraestrutura | Ubuntu Server ARM64 |

# 3. Arquitetura de software

A arquitetura será dividida em quatro camadas principais.

## 3.1 Frontend Angular

Responsável por toda a experiência visual e interação do usuário.

Módulos:

- Dashboard
- Aplicações
- Descoberta de aplicações
- Namespaces
- Containers e Pods
- Rede
- Armazenamento
- Monitoramento
- Atividades e logs
- Configurações
- Autenticação

## 3.2 Backend FastAPI

Responsável pela lógica de negócio e comunicação com o Kubernetes.

Serviços:

**ApplicationService**
- Cadastro de aplicações.
- Atualização dos dados visuais.
- Favoritos e categorias.
- Controle de visibilidade.

**DiscoveryService**
- Descoberta de namespaces.
- Identificação de Deployments.
- Identificação de Services.
- Identificação de Ingress.
- Associação dos recursos às aplicações.

**KubernetesService**
- Consulta de recursos.
- Reinicialização de Deployments.
- Escalonamento de réplicas.
- Consulta de Pods.
- Consulta de logs.
- Consulta de eventos.

**MetricsService**
- CPU.
- Memória RAM.
- Armazenamento.
- Rede.
- Métricas dos workloads.

**StorageService**
- Persistent Volumes.
- Persistent Volume Claims.
- Capacidade e utilização.
- Situação dos volumes.

## 3.3 Banco de dados

O PostgreSQL armazenará os dados próprios da plataforma.

Não será utilizado como fonte de verdade para o estado do Kubernetes. O estado operacional será sempre consultado no cluster.

## 3.4 Integração K3s

O backend utilizará a API oficial do Kubernetes através do cliente Python.

A comunicação será feita com autenticação por ServiceAccount e RBAC, evitando acesso administrativo irrestrito ao cluster.

# 4. Estrutura de diretórios

```text
home-server-manager/
│
├── frontend/
│   ├── src/app/
│   │   ├── core/
│   │   │   ├── auth/
│   │   │   ├── guards/
│   │   │   └── services/
│   │   │
│   │   ├── layout/
│   │   │   ├── sidebar/
│   │   │   ├── header/
│   │   │   └── main-layout/
│   │   │
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   ├── applications/
│   │   │   ├── discovery/
│   │   │   ├── namespaces/
│   │   │   ├── containers/
│   │   │   ├── storage/
│   │   │   ├── network/
│   │   │   ├── monitoring/
│   │   │   ├── activity/
│   │   │   └── settings/
│   │   │
│   │   └── shared/
│   │       ├── components/
│   │       ├── models/
│   │       └── pipes/
│   │
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── kubernetes/
│   │   ├── workers/
│   │   └── websocket/
│   │
│   └── Dockerfile
│
├── database/
│   └── migrations/
│
├── deployment/
│   ├── namespace.yaml
│   ├── backend.yaml
│   ├── frontend.yaml
│   ├── postgres.yaml
│   ├── rbac.yaml
│   └── ingress.yaml
│
├── documentation/
│
└── README.md
```

# 5. Funcionalidades do sistema

## 5.1 Dashboard

A página inicial deverá exibir:

- Total de aplicações cadastradas.
- Aplicações online e offline.
- Consumo de CPU.
- Consumo de memória.
- Utilização do armazenamento.
- Status do cluster.
- Quantidade de Pods.
- Aplicações favoritas.
- Últimas atividades.

## 5.2 Gerenciamento de aplicações

Cada aplicação terá:

- Nome.
- Nome de exibição.
- Ícone.
- Descrição.
- Categoria.
- Namespace.
- URL de acesso.
- Status.
- Deployment associado.
- Services associados.
- Data de cadastro.
- Favorito.
- Visibilidade no Dashboard.

Ações disponíveis:

- Abrir aplicação.
- Consultar detalhes.
- Consultar logs.
- Reiniciar Deployment.
- Parar ou escalar Deployment.
- Editar informações visuais.
- Remover do Dashboard.

Importante: remover do Dashboard não deverá excluir recursos do Kubernetes.

## 5.3 Descoberta automática

O sistema deverá consultar periodicamente o K3s.

Fluxo:

1. Consultar namespaces.
2. Consultar Deployments.
3. Consultar Services.
4. Consultar Ingress.
5. Identificar associações através de labels e selectors.
6. Cruzar os resultados com o banco de dados.
7. Exibir recursos ainda não cadastrados.
8. Permitir confirmação e personalização pelo usuário.

A descoberta não deverá cadastrar automaticamente todos os Pods como aplicações independentes.

A entidade principal será a aplicação, que poderá possuir vários recursos Kubernetes.

## 5.4 Monitoramento

Indicadores:

- CPU total.
- Memória total e utilizada.
- Disco.
- Rede.
- Temperatura, quando suportada.
- Pods em execução.
- Pods com falhas.
- Reinicializações.
- Estado dos Deployments.

Prometheus poderá fornecer métricas históricas. Para informações de hardware, poderá ser utilizado um agente como Node Exporter.

# 6. Modelo de dados

## Tabela applications

| Campo | Tipo |
|---|---|
| id | Integer |
| name | String |
| display_name | String |
| description | Text |
| icon | String |
| category | String |
| namespace | String |
| access_url | String |
| favorite | Boolean |
| visible | Boolean |
| discovery_source | String |
| created_at | DateTime |
| updated_at | DateTime |

## Tabela kubernetes_resources

| Campo | Tipo |
|---|---|
| id | Integer |
| application_id | FK |
| resource_type | String |
| resource_name | String |
| namespace | String |
| status | String |
| last_sync | DateTime |

## Tabela app_events

| Campo | Tipo |
|---|---|
| id | Integer |
| application_id | FK |
| event_type | String |
| message | Text |
| created_at | DateTime |

## Tabela users

| Campo | Tipo |
|---|---|
| id | Integer |
| username | String |
| password_hash | String |
| is_active | Boolean |
| created_at | DateTime |

## Tabela settings

| Campo | Tipo |
|---|---|
| id | Integer |
| setting_key | String |
| setting_value | JSON |
| updated_at | DateTime |

# 7. API REST

Prefixo: `/api/v1`

| Método | Endpoint | Função |
|---|---|---|
| GET | `/dashboard` | Dados do Dashboard |
| GET | `/applications` | Listar aplicações |
| POST | `/applications` | Cadastrar aplicação |
| GET | `/applications/{id}` | Detalhes |
| PUT | `/applications/{id}` | Atualizar cadastro |
| DELETE | `/applications/{id}` | Remover cadastro |
| POST | `/applications/discover` | Executar descoberta |
| GET | `/applications/discovered` | Aplicações descobertas |
| GET | `/namespaces` | Listar namespaces |
| GET | `/kubernetes/deployments` | Listar Deployments |
| GET | `/kubernetes/pods` | Listar Pods |
| GET | `/kubernetes/services` | Listar Services |
| GET | `/kubernetes/ingresses` | Listar Ingress |
| GET | `/kubernetes/events` | Consultar eventos |
| GET | `/storage` | Informações de volumes |
| GET | `/monitoring/metrics` | Métricas |
| GET | `/applications/{id}/logs` | Consultar logs |
| POST | `/applications/{id}/restart` | Reiniciar Deployment |

WebSocket:

`/ws/dashboard`

Responsável por atualizar status, métricas e progresso de operações.

# 8. Segurança

Requisitos obrigatórios:

- Autenticação de usuários.
- Senhas armazenadas com hash seguro.
- Sessões protegidas.
- HTTPS.
- RBAC no Kubernetes.
- ServiceAccount específica para a plataforma.
- Permissões mínimas necessárias.
- Proteção contra CSRF quando aplicável.
- Validação dos parâmetros recebidos.
- Registro das operações administrativas.
- Segregação entre leitura e operações de escrita.

O backend não deverá executar comandos arbitrários de shell recebidos do frontend.

As operações Kubernetes deverão passar por serviços específicos e validados.

# 9. Implantação no K3s

O próprio Home Server Manager será executado dentro do cluster K3s.

Componentes previstos:

- Namespace `home-server-manager`.
- Deployment Angular.
- Deployment FastAPI.
- PostgreSQL com armazenamento persistente.
- ServiceAccount.
- Role e RoleBinding.
- Ingress para acesso web.
- PVC para persistência.

O PostgreSQL deverá utilizar volume persistente. Em um Raspberry Pi, é recomendável utilizar SSD USB em vez de depender exclusivamente do microSD.

Todos os containers deverão possuir imagens compatíveis com ARM64.

# 10. Fases de desenvolvimento

## Fase 1 — Fundação
- Criar estrutura Angular.
- Criar estrutura FastAPI.
- Configurar PostgreSQL.
- Configurar autenticação.
- Criar layout principal.

## Fase 2 — Integração K3s
- Configurar Kubernetes Python Client.
- Implementar ServiceAccount e RBAC.
- Implementar descoberta de namespaces.
- Implementar descoberta de Deployments, Services e Ingress.
- Implementar associação de recursos.

## Fase 3 — Aplicações
- Criar cadastro de aplicações.
- Criar cards.
- Criar personalização de ícones.
- Criar favoritos.
- Criar acesso por URL.
- Criar gerenciamento de visibilidade.

## Fase 4 — Monitoramento
- Implementar métricas de hardware.
- Integrar Prometheus.
- Exibir métricas dos workloads.
- Implementar gráficos.
- Criar histórico de eventos.

## Fase 5 — Administração
- Reiniciar Deployments.
- Escalar réplicas.
- Consultar logs.
- Consultar eventos.
- Administrar armazenamento.
- Implementar histórico de operações.

## Fase 6 — Finalização
- Ajustar responsividade.
- Otimizar consumo de memória.
- Implementar backup.
- Implementar atualização da plataforma.
- Criar documentação de instalação.

# 11. Critérios de aceite do MVP

O MVP será considerado funcional quando:

1. O usuário conseguir acessar o painel pelo navegador.
2. A plataforma conseguir conectar ao K3s.
3. Os namespaces e Deployments existentes forem identificados.
4. O usuário conseguir cadastrar e personalizar aplicações.
5. Os cards exibirem o estado real das aplicações.
6. O usuário conseguir abrir suas aplicações.
7. O sistema apresentar métricas básicas do servidor.
8. O usuário conseguir consultar logs.
9. A plataforma não excluir recursos Kubernetes ao remover um card.
10. O sistema funcionar em ARM64 no Raspberry Pi 4.

# 12. Decisões técnicas pendentes

Antes de iniciar a implementação, precisamos confirmar:

- Memória RAM do Raspberry Pi.
- Tipo de armazenamento.
- Se o K3s possui apenas um nó ou vários.
- Se o Traefik padrão está habilitado.
- Quais aplicações já estão instaladas.
- Como você pretende acessar o painel: somente rede local ou também remotamente.

# 13. Diretriz principal do produto

O Home Server Manager não deve tentar substituir o K3s.

Ele deverá oferecer uma interface amigável sobre o Kubernetes, permitindo que o usuário tenha controle visual sobre as aplicações e os serviços existentes no servidor.

**Princípio fundamental: qualquer aplicação que esteja rodando no K3s poderá ser descoberta, organizada e apresentada no painel, independentemente de como foi instalada.**