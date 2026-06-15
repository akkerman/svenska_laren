import { useState } from "react";

export function useTTS() {
  const [playing, setPlaying] = useState(false);

  const speak = async (text: string) => {
    if (!text.trim()) return;

    try {
      setPlaying(true);
      const response = await fetch(`/api/tts/speak?text=${encodeURIComponent(text)}`);
      if (!response.ok) throw new Error("TTS failed");

      const audio = await response.blob();
      const audioUrl = URL.createObjectURL(audio);
      const audioElement = new Audio(audioUrl);

      audioElement.onended = () => setPlaying(false);
      audioElement.play();
    } catch (error) {
      console.error("TTS error:", error);
      setPlaying(false);
    }
  };

  return { speak, playing };
}
