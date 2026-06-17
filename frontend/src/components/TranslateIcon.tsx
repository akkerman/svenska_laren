export function TranslateIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Blue box with X (Dutch/left) */}
      <rect x="8" y="24" width="28" height="28" rx="6" fill="#2563eb" />
      <text
        x="22"
        y="48"
        fontSize="20"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        ×
      </text>

      {/* Dark box with A (Swedish/right) */}
      <rect x="28" y="12" width="28" height="28" rx="6" fill="#374151" />
      <text
        x="42"
        y="36"
        fontSize="20"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        A
      </text>

      {/* Arrow from blue to dark (top right) */}
      <path
        d="M 20 18 Q 30 8 40 12"
        stroke="#374151"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      <polygon points="42,10 44,18 36,15" fill="#374151" />

      {/* Arrow from dark to blue (bottom left) */}
      <path
        d="M 44 46 Q 34 56 24 52"
        stroke="#2563eb"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      <polygon points="22,54 20,46 28,49" fill="#2563eb" />
    </svg>
  );
}
