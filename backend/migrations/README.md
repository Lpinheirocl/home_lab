# Migrações

Executar a partir de `backend/`:

```bash
alembic upgrade head
```

A URL do banco é configurada por `HSM_DATABASE_URL`. Nenhuma migração é executada automaticamente pela API.
