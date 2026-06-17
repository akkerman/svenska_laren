import requests
import json
import os
from typing import Generator

# Support Docker: OLLAMA_URL can be set via environment
# Default: localhost (dev), or host.docker.internal (Docker on Mac/Windows)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = "alibayram/erurollm-9b-instruct"

def generate(prompt: str, system: str = "") -> str:
    """Generate text using Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "system": system, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")

def chat(messages: list, system: str = "") -> str:
    """Chat with Ollama using message history."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result.get("message", {}).get("content", "").strip()
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")

def stream_chat(messages: list, system: str = "") -> Generator[str, None, None]:
    """Stream chat responses from Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": True},
            timeout=120,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if chunk.get("message", {}).get("content"):
                    yield chunk["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Ollama streaming error: {e}")
