# Arquitetura inicial

O projeto é um monorepo com frontend Angular, backend FastAPI e PostgreSQL.
Nesta fase o backend possui apenas o health check e a fábrica do cliente Kubernetes.
`HSM_KUBERNETES_ENABLED` permanece desativado por padrão e nenhum recurso do cluster é consultado ou alterado durante a inicialização.
