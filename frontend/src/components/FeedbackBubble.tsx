import React from "react";

interface FeedbackBubbleProps {
  score?: number;
  feedback: string;
  corrected?: string;
}

export function FeedbackBubble({
  score,
  feedback,
  corrected,
}: FeedbackBubbleProps) {
  const getScoreColor = (score?: number) => {
    if (!score) return "bg-gray-100";
    if (score >= 4) return "bg-green-100 border-green-300";
    if (score >= 3) return "bg-yellow-100 border-yellow-300";
    return "bg-red-100 border-red-300";
  };

  return (
    <div className={`border-l-4 p-4 rounded ${getScoreColor(score)}`}>
      {score && (
        <div className="mb-2 font-semibold text-sm">
          Score: {score}/5
        </div>
      )}
      <p className="text-gray-800 mb-2">{feedback}</p>
      {corrected && (
        <div className="text-sm text-gray-700 italic">
          <strong>Verbeterd:</strong> {corrected}
        </div>
      )}
    </div>
  );
}
