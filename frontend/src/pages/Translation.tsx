import { useState, useRef } from "react";
import {
  generateTranslation,
  evaluateTranslation,
  type TranslationResponse,
  type EvaluationResponse,
} from "../api";
import { useSettings } from "../context/SettingsContext";
import { FeedbackBubble } from "../components/FeedbackBubble";
import { SwedishChars } from "../components/SwedishChars";

const languageNames: Record<string, string> = {
  Dutch: "Nederlands",
  Swedish: "Zweeds",
  English: "Engels",
};

export function Translation() {
  const { difficulty } = useSettings();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [direction, setDirection] = useState("nl_to_se");
  const [topic, setTopic] = useState("");
  const [sentence, setSentence] = useState<TranslationResponse | null>(null);
  const [userAttempt, setUserAttempt] = useState("");
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateSentence = async () => {
    setLoading(true);
    setSentence(null);
    setUserAttempt("");
    setEvaluation(null);

    try {
      const generated = await generateTranslation(
        direction,
        difficulty,
        topic || undefined
      );
      setSentence(generated);
    } catch (error) {
      console.error("Failed to generate sentence:", error);
    }
    setLoading(false);
  };

  const handleEvaluate = async () => {
    if (!sentence || !userAttempt) return;

    setLoading(true);
    try {
      const result = await evaluateTranslation(
        sentence.sentence,
        userAttempt,
        direction,
        difficulty
      );
      setEvaluation(result);
    } catch (error) {
      console.error("Failed to evaluate:", error);
    }
    setLoading(false);
  };

  const handleCharClick = (char: string) => {
    setUserAttempt(userAttempt + char);
    textareaRef.current?.focus();
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-green-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-green-900 mb-8">Vertalen</h1>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Richting
              </label>
              <select
                value={direction}
                onChange={(e) => setDirection(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="nl_to_se">Nederlands → Zweeds</option>
                <option value="se_to_nl">Zweeds → Nederlands</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Onderwerp (optioneel)
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGenerateSentence()}
                placeholder="bijv. eten, reizen, familie"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <button
            onClick={handleGenerateSentence}
            disabled={loading}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-lg transition disabled:opacity-50 min-h-12"
          >
            {loading ? "Genereren..." : "Zin genereren"}
          </button>
        </div>

        {sentence && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="mb-6 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
              <p className="text-sm text-gray-600 mb-2">
                Vertaal deze {languageNames[sentence.language_from] || sentence.language_from} zin naar{" "}
                {languageNames[sentence.language_to] || sentence.language_to}:
              </p>
              <p className="text-2xl font-bold text-gray-800">
                {sentence.sentence}
              </p>
            </div>

            <SwedishChars onCharClick={handleCharClick} />
            <textarea
              ref={textareaRef}
              value={userAttempt}
              onChange={(e) => setUserAttempt(e.target.value)}
              placeholder="Voer je vertaling in..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-green-500 min-h-24"
            />

            <button
              onClick={handleEvaluate}
              disabled={loading || !userAttempt.trim()}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-lg transition disabled:opacity-50 min-h-12"
            >
              {loading ? "Evalueren..." : "Antwoord controleren"}
            </button>
          </div>
        )}

        {evaluation && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <FeedbackBubble
              score={evaluation.score}
              feedback={evaluation.feedback}
              corrected={evaluation.corrected}
            />

            <button
              onClick={handleGenerateSentence}
              className="w-full mt-6 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-lg transition min-h-12"
            >
              Volgende zin
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
