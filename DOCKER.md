# Docker Setup voor svenska-laren

## Requirements
- Docker 20.10+
- Docker Compose 2.0+

## Starten

```bash
docker compose up
```

Dit zal:
- Backend (FastAPI) bouwen en starten op `http://localhost:8000`
- Frontend (React/Vite) bouwen en starten op `http://localhost:5173`
- De bestaande SQLite database gebruiken (local mount)

## Ports

| Service  | Port | URL                    |
|----------|------|------------------------|
| Backend  | 8000 | http://localhost:8000  |
| Frontend | 5173 | http://localhost:5173  |

## Services

- **backend**: FastAPI server met SQLAlchemy, Pydantic, gTTS
- **frontend**: React + Vite dev server met hot-reload

## Database

De SQLite database (`svenska_laren.db`) in `/backend/` wordt gemount in beide containers en persisted tussen restarts.

## Hot-reload

- **Frontend**: `src/` en `public/` directories zijn volume-mounted, dus wijzigingen zijn direct zichtbaar
- **Backend**: Om wijzigingen live te zien, moet je de container herstarten: `docker compose restart backend`

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
