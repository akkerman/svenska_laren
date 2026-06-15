from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
import os
import tempfile
import subprocess
from pathlib import Path

router = APIRouter(prefix="/api/tts", tags=["tts"])

# Piper model for Swedish (sv-SE)
PIPER_MODEL = "sv_SE-nathalie"
PIPER_VOICE = "sv_SE-nathalie"
PIPER_DATA_DIR = str(Path.home() / ".local" / "share" / "piper")

@router.get("/speak")
def text_to_speech(text: str = Query(...)):
    """Convert Swedish text to speech using Piper TTS."""
    if not text or len(text) > 500:
        raise ValueError("Text must be between 1 and 500 characters")

    # Create temporary file for audio output
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Run piper to generate speech
        process = subprocess.run(
            ["piper", "--model", PIPER_VOICE, "--data-dir", PIPER_DATA_DIR, "--output-file", output_file],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True
        )

        # Return the audio file
        return FileResponse(
            output_file,
            media_type="audio/wav",
            headers={"Content-Disposition": "inline"}
        )
    except subprocess.CalledProcessError as e:
        # Clean up temp file if error
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise RuntimeError(f"Piper TTS failed: {e.stderr.decode()}")
