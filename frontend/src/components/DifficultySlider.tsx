import React, { useRef } from "react";
import { useSettings } from "../context/SettingsContext";

export function DifficultySlider() {
  const { difficulty, setDifficulty } = useSettings();
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setDifficulty(value);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      // Debounced update already happens in context
    }, 300);
  };

  const getDifficultyLabel = () => {
    if (difficulty < 0.3) return "Beginner";
    if (difficulty < 0.6) return "Gemiddeld";
    if (difficulty < 0.85) return "Gevorderd";
    return "Native";
  };

  return (
    <div className="flex items-center gap-2 w-full">
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={difficulty}
        onChange={handleChange}
        className="w-full h-2 bg-blue-300 rounded-lg appearance-none cursor-pointer"
      />
      <span className="text-sm font-medium whitespace-nowrap">
        {getDifficultyLabel()}
      </span>
    </div>
  );
}
