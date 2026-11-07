# WHACK 26

```mermaid
sequenceDiagram
    Frontend (Svelte)<<->>Pocketbase (JS): auth
    Frontend (Svelte)<<->>Pocketbase (JS): db stuff?
    Frontend (Svelte)->>Pocketbase (JS): Who would win?
    Pocketbase (JS)->>FastAPI (Python): Who would win?
    FastAPI (Python)->>Ollama (AI): Who would win?
```

- Frontend (Svelte)
- Backend (Python with fastapi)
- pocketbase (with js extension)