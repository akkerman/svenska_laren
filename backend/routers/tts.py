from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
import tempfile
from gtts import gTTS

router = APIRouter(prefix="/api/tts", tags=["tts"])

@router.get("/speak")
def text_to_speech(text: str = Query(...)):
    """Convert Swedish text to speech using Google TTS."""
    if not text or len(text) > 500:
        raise ValueError("Text must be between 1 and 500 characters")

    try:
        # Generate speech using Google TTS
        tts = gTTS(text=text, lang="sv", slow=False)

        # Create temporary file for audio output
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            output_file = tmp.name
            tts.save(output_file)

        # Return the audio file
        return FileResponse(
            output_file,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        raise RuntimeError(f"TTS failed: {str(e)}")
