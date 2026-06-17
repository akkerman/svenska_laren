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
        y="48"
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
        y="30"
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
        <line x1="26" y1="38" x2="32" y2="28" stroke="#2563eb" strokeWidth="3" strokeLinecap="round" />
        <polygon points="32,28 28,30 30,24" fill="#2563eb" />
      </g>

      {/* Arrow from SE to NL (going down-left) */}
      <g>
        <line x1="36" y1="24" x2="24" y2="42" stroke="#374151" strokeWidth="3" strokeLinecap="round" />
        <polygon points="24,42 28,40 26,46" fill="#374151" />
      </g>
    </svg>
  );
}
