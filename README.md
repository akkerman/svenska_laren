# Svenska Lären — Learn Swedish with AI

A personal Swedish language learning app with flashcards (Leitner box), translation exercises, and free conversation powered by local Ollama AI.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Ollama running with `alibayram/erurollm-9b-instruct` model:
  ```bash
  ollama pull alibayram/erurollm-9b-instruct
  ollama serve
  ```
- Piper TTS Swedish voice:
  ```bash
  piper --download-dir ~/.local/share/piper_phoneme_dict --model sv_SE-nathalie-medium
  ```

### Setup & Run

**Backend (Python FastAPI)**
```bash
cd backend
pipenv install
pipenv run uvicorn main:app --reload --port 8003
```

**Frontend (React + Vite)**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Features

- **Flashcards** — Spaced repetition with Leitner box (5 boxes, adaptive intervals)
- **Translation** — Generate sentences in Dutch/Swedish, translate both directions, get feedback
- **Conversation** — Free-form chat with AI Swedish partner, corrections on demand
- **Difficulty Slider** — Adjust difficulty 0–1; affects vocabulary selection, sentence complexity, conversation level
- **Mobile-friendly** — Responsive design, works on phones

## Project Structure

```
svenska-laren/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # SQLAlchemy + sqlite
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── ollama.py            # Ollama HTTP client
│   ├── routers/             # API endpoints
│   ├── data/wordlist.json   # ~150 Swedish words
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx          # Main component
    │   ├── api.ts           # Typed API calls
    │   ├── context/         # Settings context
    │   ├── components/      # Reusable components
    │   └── pages/           # Page components
    ├── package.json
    └── vite.config.ts
```

## API Endpoints

All endpoints under `/api`:

- `GET/PUT /settings` — Difficulty setting
- `GET /cards/due` — Cards due for review
- `GET /cards/stats` — Stats by box
- `POST /cards/answer` — Answer card (correct/wrong)
- `POST /translation/generate` — Generate sentence to translate
- `POST /translation/evaluate` — Evaluate user's translation
- `POST /conversation/start` — Start conversation session
- `POST /conversation/message` — Send message (streaming SSE)
- `GET /conversation/history/{session_id}` — Get chat history
- `DELETE /conversation/{session_id}` — Delete session

## Leitner Box Intervals

| Box | Review After |
|-----|--------------|
| 1   | 1 day        |
| 2   | 2 days       |
| 3   | 4 days       |
| 4   | 8 days       |
| 5   | Never (mastered) |

Correct answer → advance box (max 5)
Wrong answer → back to box 1

## Difficulty Levels

- **0.0–0.3**: Beginner (simple vocab, short sentences, English hints)
- **0.3–0.6**: Intermediate (mixed tenses, medium sentences)
- **0.6–0.85**: Advanced (idioms, complex grammar)
- **0.85–1.0**: Native (full speed, all corrections)

## Build for Production

```bash
cd frontend && npm run build
cd ../backend && uvicorn main:app --port 8003
# Serves app from http://localhost:8003
```

## Notes

- SQLite database auto-initializes with Swedish wordlist on first startup
- All Ollama calls timeout after 60s
- Streaming conversation uses Server-Sent Events (SSE)
- Difficulty is synced to backend but affects all requests
