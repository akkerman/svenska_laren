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

      {/* Arrow from NL to SE via L-shape */}
      <path
        d="M 32 42 L 44 42 L 44 36"
        stroke="#2563eb"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polygon points="44,32 41.9,36 46.1,36" fill="#2563eb" />
    </svg>
  );
}
