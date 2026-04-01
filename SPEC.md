# Link Shortener - Specification

## 1. Project Overview

- **Project Name**: Link Shortener API
- **Type**: REST API (FastAPI)
- **Core Functionality**: Encurtar URLs e redirecionar para URLs originais
- **Target Users**: Desenvolvedores e aplicações que precisam de encurtamento de links

## 2. Architecture

### Stack
- **Framework**: FastAPI (async)
- **Dependency Manager**: UV
- **Storage**: In-memory dict com persistência em arquivo JSON
- **Validation**: Pydantic v2

### Design Patterns
- **Repository Pattern**: Abstração do armazenamento
- **Service Layer**: Lógica de negócio separada
- **Dependency Injection**: FastAPI Depends

## 3. Data Model

```python
# Link Entity
{
    "id": str,              # UUID único
    "short_code": str,      # Código único (base62, 6-8 chars)
    "original_url": str,    # URL original
    "clicks": int,          # Contador de acessos
    "created_at": datetime,
    "expires_at": datetime | None  # Opcional
}
```

## 4. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/links` | Criar link encurtado |
| GET | `/api/links/{short_code}` | Obter info do link |
| GET | `/{short_code}` | Redirecionar para URL original |
| DELETE | `/api/links/{short_code}` | Deletar link |
| GET | `/api/links/{short_code}/stats` | Estatísticas do link |

## 5. Implementation Details

### Short Code Generation
- Base62 (a-z, A-Z, 0-9) - 6 a 8 caracteres
- Hash determinístico da URL + timestamp
- Verificação de duplicatas

### Performance Optimizations
- Lock para operações thread-safe
- Lazy loading da persistência
- Cache em memória com TTL
- Redirect 307 (temporarily moved) para performance
- Async I/O para operações de arquivo

### Storage
- Arquivo: `links.json` no diretório de dados
- Backup automático antes de menulis
- Estrutura: `{ "links": {...}, "short_codes": {...} }`

## 6. Security

- Validação de URL (scheme http/https obrigatório)
- Sanitização de input
- Rate limiting (opcional)
- CORS configurável

## 7. Project Structure

```
link-shortener/
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── link_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── link_repository.py
│   └── routes/
│       ├── __init__.py
│       └── links.py
├── data/
│   └── links.json
└── tests/
    └── test_links.py
```

## 8. Acceptance Criteria

- [ ] POST /api/links retorna short_code e URL original
- [ ] GET /{short_code} redireciona com 307
- [ ] GET /api/links/{short_code} retorna detalhes
- [ ] GET /api/links/{short_code}/stats retorna cliques
- [ ] DELETE remove o link
- [ ] Dados persistem entre reinicializações
- [ ] Aplicação inicia com UV
- [ ] Documentação OpenAPI disponível em /docs
