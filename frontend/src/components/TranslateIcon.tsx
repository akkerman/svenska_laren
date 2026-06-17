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

      {/* A in dark box */}
      <text
        x="45"
        y="30"
        fontSize="18"
        fontWeight="bold"
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
      >
        A
      </text>

      {/* Arrow pointing right-up (blue to dark) */}
      <line x1="18" y1="35" x2="32" y2="25" stroke="#2563eb" strokeWidth="3" />
      <polygon points="32,25 28,32 26,27" fill="#2563eb" />

      {/* Arrow pointing left-down (dark to blue) */}
      <line x1="40" y1="50" x2="26" y2="40" stroke="#374151" strokeWidth="3" />
      <polygon points="26,40 30,33 36,38" fill="#374151" />

      {/* X in blue box */}
      <line x1="14" y1="40" x2="22" y2="48" stroke="white" strokeWidth="3" strokeLinecap="round" />
      <line x1="22" y1="40" x2="14" y2="48" stroke="white" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
