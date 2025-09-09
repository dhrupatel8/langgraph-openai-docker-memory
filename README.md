# LangGraph + OpenAI • Live Memory UI (Docker)

Adds:
- Live session memory panel (UI)
- Session IDs via localStorage
- Archive button (server keeps old memory)
- UI Clear button (client-only)
- Disk persistence in MEMORY_DIR (/data via docker-compose)

## Quickstart
cp .env .env
# add your OPENAI_API_KEY
docker compose up --build
open http://localhost:8080

## Endpoints
POST /chat?session_id=...
GET  /memory?session_id=...
GET  /memory/archives?session_id=...
GET  /memory/archive/{archive_id}?session_id=...
POST /memory/archive?session_id=...
GET  /graph.mmd
GET  /graph

![DEMO](demo.gif)