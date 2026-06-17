# Docker Setup voor svenska-laren

## Requirements
- Docker 20.10+
- Docker Compose 2.0+

## Starten

```bash
docker compose up
```

Dit zal:
- Backend (FastAPI) bouwen en starten (niet geëxposed op host)
- Frontend (React/Vite) bouwen en starten op `http://localhost:5173`
- De bestaande SQLite database gebruiken (local mount)

## Ports

| Service  | URL                    | Notitie                                    |
|----------|------------------------|------------------------------------------|
| Frontend | http://localhost:5173  | Via host, gebruikt `/api` proxy naar backend |
| Backend  | —                      | Alleen beschikbaar in Docker network       |

## Services

- **backend**: FastAPI server met SQLAlchemy, Pydantic, gTTS
- **frontend**: React + Vite dev server met hot-reload

## Database

De SQLite database (`svenska_laren.db`) in `/backend/` wordt gemount in beide containers en persisted tussen restarts.

## Hot-reload

- **Frontend**: `src/` en `public/` directories zijn volume-mounted, dus wijzigingen zijn direct zichtbaar
- **Backend**: Wijzigingen vereisen container restart: `docker compose restart backend`

## API Access

Frontend communiceert met backend via het interne Docker network (`http://backend:8000`). Je hoeft de backend niet handmatig aan te roepen - alles gaat via de frontend op port 5173.

## Ollama

Backend verwacht Ollama op `http://host.docker.internal:11434` (Mac/Windows) of `http://localhost:11434` (native Linux).

Voor Linux (host.docker.internal werkt niet):
```bash
OLLAMA_URL=http://172.17.0.1:11434 docker compose up
```

Of voeg toe in `docker-compose.yml` service backend:
```yaml
environment:
  - OLLAMA_URL=http://172.17.0.1:11434
```

## Stoppen

```bash
docker compose down
```

Services stoppen. Data persists (database niet gewist).

## Logs

```bash
docker compose logs -f          # Alle services
docker compose logs -f backend  # Alleen backend
docker compose logs -f frontend # Alleen frontend
```

## Rebuild

Als je dependencies hebt gewijzigd:

```bash
docker compose build --no-cache
docker compose up
```
