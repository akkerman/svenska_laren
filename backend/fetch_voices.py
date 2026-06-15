"""Download required Piper TTS voices for Swedish language."""

import piper

VOICES = ["sv_SE-nathalie-medium"]

def main():
    print("Downloading Piper TTS voices...")
    piper.download_voices(VOICES)
    print(f"✓ Downloaded: {', '.join(VOICES)}")

if __name__ == "__main__":
    main()
