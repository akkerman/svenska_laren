"""Download required Piper TTS voices for Swedish language."""

import urllib.request
import json
from pathlib import Path

VOICES = ["sv_SE-nathalie"]

def main():
    print("Downloading Piper TTS voices...")

    data_dir = Path.home() / ".local" / "share" / "piper"
    data_dir.mkdir(parents=True, exist_ok=True)

    for voice in VOICES:
        voice_dir = data_dir / voice
        if voice_dir.exists():
            print(f"✓ {voice} already exists")
            continue

        print(f"  Downloading {voice}...")
        voice_dir.mkdir(parents=True, exist_ok=True)

        # Download voice model and config from Piper repo
        base_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{voice}"

        for filename in [f"{voice}.onnx", f"{voice}.onnx.json"]:
            url = f"{base_url}/{filename}"
            output_path = voice_dir / filename

            try:
                print(f"    Fetching {filename}...")
                urllib.request.urlretrieve(url, output_path)
                print(f"    ✓ {filename}")
            except Exception as e:
                print(f"    ✗ Failed to download {filename}: {e}")
                return

    print(f"✓ All voices ready!")

if __name__ == "__main__":
    main()
