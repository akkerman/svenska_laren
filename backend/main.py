from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from database import init_db
from routers import settings, vocabulary, leitner, translation, conversation

app = FastAPI(title="Svenska Lären", description="Swedish Learning App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(settings.router)
app.include_router(vocabulary.router)
app.include_router(leitner.router)
app.include_router(translation.router)
app.include_router(conversation.router)

frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}
