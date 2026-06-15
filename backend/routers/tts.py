from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile
import subprocess
from pathlib import Path

router = APIRouter(prefix="/api/tts", tags=["tts"])

# Piper model for Swedish (sv-SE) - disabled for now due to voice model availability
TTS_ENABLED = False

@router.get("/speak")
def text_to_speech(text: str = Query(...)):
    """Convert Swedish text to speech using Piper TTS (currently disabled)."""
    if not TTS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Text-to-speech is not configured. Swedish voice models are optional."
        )

    if not text or len(text) > 500:
        raise ValueError("Text must be between 1 and 500 characters")

    # Create temporary file for audio output
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Run piper to generate speech
        process = subprocess.run(
            ["piper", "--model", "sv_SE-nathalie", "--output-file", output_file],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True,
            timeout=30
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
        stderr = e.stderr.decode() if e.stderr else str(e)
        raise HTTPException(status_code=500, detail=f"TTS failed: {stderr}")
