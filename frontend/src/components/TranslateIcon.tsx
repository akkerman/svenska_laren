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
      <rect x="6" y="28" width="26" height="26" rx="6" fill="#2563eb" />

      {/* Dark box (right/top) */}
      <rect x="32" y="10" width="26" height="26" rx="6" fill="#374151" />

      {/* SE in dark box */}
      <text
        x="45"
        y="30"
        fontSize="14"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        SE
      </text>

      {/* Arrow pointing right-up (NL to SE) */}
      <path
        d="M 32 42 L 38 28"
        stroke="#2563eb"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />
      <polygon points="38,28 34,31 36,26" fill="#2563eb" />

      {/* Arrow pointing left-down (SE to NL) */}
      <path
        d="M 34 36 L 28 50"
        stroke="#374151"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />
      <polygon points="28,50 32,47 30,52" fill="#374151" />

      {/* NL in blue box */}
      <text
        x="19"
        y="48"
        fontSize="14"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        NL
      </text>
    </svg>
  );
}
