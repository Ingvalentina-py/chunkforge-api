# ChunkForge API

API REST para preparar documentos (chunking con DeepSeek) y generar embeddings locales.

> **Documentación completa de endpoints:** ver **[ENDPOINTS.md](./ENDPOINTS.md)** (referencia canónica de los 3 endpoints).

**Enlaces rápidos**

| Recurso | URL |
|---------|-----|
| Health | `GET /` |
| Swagger | `/docs` |
| API v1 | `/api/v1` |
| Guía frontend | [FRONTEND.md](./FRONTEND.md) |
| Postman | [../postman/](../postman/) |

**Endpoints v1**

1. `POST /api/v1/documents/prepare` — documento → chunks
2. `POST /api/v1/documents/{document_id}/embeddings` — chunks → vectores
3. `POST /api/v1/embed` — oración → vector

Detalle de contratos, ejemplos cURL y errores: **[ENDPOINTS.md](./ENDPOINTS.md)**.
