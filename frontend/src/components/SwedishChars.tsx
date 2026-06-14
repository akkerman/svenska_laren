import React from "react";

interface SwedishCharsProps {
  onCharClick: (char: string) => void;
}

export function SwedishChars({ onCharClick }: SwedishCharsProps) {
  const chars = ["å", "ä", "ö"];

  return (
    <div className="flex gap-2 mb-3">
      <span className="text-xs text-gray-600 font-semibold">Zweeds:</span>
      {chars.map((char) => (
        <button
          key={char}
          onClick={() => onCharClick(char)}
          className="bg-blue-200 hover:bg-blue-300 text-blue-900 font-bold px-3 py-1 rounded text-sm transition"
        >
          {char}
        </button>
      ))}
    </div>
  );
}
