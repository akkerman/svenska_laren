"""Download required Piper TTS voices for Swedish language."""

import subprocess
import sys

VOICES = ["sv_SE-nathalie"]

def main():
    print("Setting up Piper TTS voices...")

    for voice in VOICES:
        print(f"  Downloading {voice}...")
        try:
            # Use piper's Python API to download
            result = subprocess.run(
                [sys.executable, "-c", f"from piper.voice import PiperVoice; PiperVoice.load('{voice}')"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print(f"✓ {voice} ready")
            else:
                print(f"✗ Failed to load {voice}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
        except Exception as e:
            print(f"✗ Error: {e}")
            return

    print(f"✓ All voices ready!")

if __name__ == "__main__":
    main()
