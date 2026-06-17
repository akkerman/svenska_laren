export function TranslateIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Blue box (left/bottom) */}
      <rect x="8" y="30" width="24" height="24" rx="5" fill="#2563eb" />

      {/* Dark box (right/top) */}
      <rect x="32" y="12" width="24" height="24" rx="5" fill="#374151" />

      {/* NL in blue box */}
      <text
        x="20"
        y="42"
        fontSize="13"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        NL
      </text>

      {/* SE in dark box */}
      <text
        x="44"
        y="24"
        fontSize="13"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        SE
      </text>

      {/* Arrow from NL to SE (going up-right) */}
      <g>
        <line x1="30" y1="36" x2="36" y2="28" stroke="#2563eb" strokeWidth="3" strokeLinecap="round" />
        <polygon points="36,28 32,32 34,26" fill="#2563eb" />
      </g>

      {/* Arrow from SE to NL (going down-left) */}
      <g>
        <line x1="34" y1="20" x2="28" y2="48" stroke="#374151" strokeWidth="3" strokeLinecap="round" />
        <polygon points="28,48 32,44 30,50" fill="#374151" />
      </g>
    </svg>
  );
}
