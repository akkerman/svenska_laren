import { useState, useEffect } from "react";
import { getDueCards, answerCard, getStats, updateCardNotes } from "../api";
import { useSettings } from "../context/SettingsContext";
import { useTTS } from "../hooks/useTTS";
import type { WordCard, CardStats } from "../api";

export function Flashcard() {
  const { difficulty } = useSettings();
  const { speak, playing } = useTTS();
  const [cards, setCards] = useState<WordCard[]>([]);
  const [stats, setStats] = useState<CardStats | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [direction, setDirection] = useState<"se_nl" | "nl_se">("se_nl");
  const [editingNotes, setEditingNotes] = useState(false);
  const [notesInput, setNotesInput] = useState("");

  useEffect(() => {
    loadCards();
  }, [difficulty, direction]);

  const loadCards = async () => {
    setLoading(true);
    try {
      const dueCards = await getDueCards(direction);
      const cardStats = await getStats(direction);
      setCards(dueCards);
      setStats(cardStats);
      setCurrentIndex(0);
      setFlipped(false);
    } catch (error) {
      console.error("Failed to load cards:", error);
    }
    setLoading(false);
  };

  const handleAnswer = async (correct: boolean) => {
    const card = cards[currentIndex];
    if (!card) return;

    try {
      await answerCard(card.id, correct);
      await loadCards();
    } catch (error) {
      console.error("Failed to save answer:", error);
    }
  };

  const handleSaveNotes = async () => {
    const card = cards[currentIndex];
    if (!card) return;

    try {
      await updateCardNotes(card.id, notesInput);
      await loadCards();
      setEditingNotes(false);
    } catch (error) {
      console.error("Failed to save notes:", error);
    }
  };


  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-xl text-gray-600">Flitskaarten laden...</p>
      </div>
    );
  }

  if (!cards || cards.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800 mb-4">
            🎉 Geen kaarten om te reviewen!
          </p>
          <p className="text-gray-600">Prima gedaan! Kom later terug.</p>
        </div>
      </div>
    );
  }

  const card = cards[currentIndex];

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-4xl font-bold text-blue-900">Flitskaarten</h1>
            <button
              onClick={() => {
                setDirection(direction === "se_nl" ? "nl_se" : "se_nl");
                setCurrentIndex(0);
                setFlipped(false);
              }}
              className="text-sm bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition min-h-10"
            >
              {direction === "se_nl" ? "🔄 NL→SE" : "🔄 SE→NL"}
            </button>
          </div>
          {stats && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
                  <p className="text-sm text-gray-600">Totaal woorden</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-2xl font-bold text-green-600">
                    {stats.mastered}
                  </p>
                  <p className="text-sm text-gray-600">Beheerst</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-2xl font-bold text-orange-600">
                    {cards.length}
                  </p>
                  <p className="text-sm text-gray-600">Vandaag te doen</p>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 shadow">
                <p className="text-sm font-semibold text-gray-700 mb-3">Verdeling per box:</p>
                <div className="grid grid-cols-5 gap-2 text-center text-xs">
                  {stats.per_box.map((count, i) => (
                    <div key={i} className="bg-blue-50 rounded p-2">
                      <p className="font-bold text-blue-600">{count}</p>
                      <p className="text-gray-600">Box {i + 1}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-col items-center">
          <div className="w-full max-w-sm">
            <div
              onClick={() => setFlipped(!flipped)}
              className="w-full h-64 bg-white rounded-lg shadow-lg cursor-pointer flex items-center justify-center transform transition-transform duration-300 hover:shadow-xl mb-2"
            >
              <div className="text-center px-8">
                <p className="text-sm text-gray-500 mb-2">
                  {direction === "se_nl"
                    ? flipped ? "Nederlands" : "Zweeds"
                    : flipped ? "Zweeds" : "Nederlands"
                  }
                </p>
                <p className="text-4xl font-bold text-blue-900">
                  {direction === "se_nl"
                    ? flipped ? card.dutch : card.swedish
                    : flipped ? card.swedish : card.dutch
                  }
                </p>
                {card.notes && (
                  <p className="text-xs text-blue-500 italic mt-3">({card.notes})</p>
                )}
                <p className="text-xs text-gray-400 mt-4">Klik om om te draaien</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setEditingNotes(!editingNotes);
                  setNotesInput(card.notes || "");
                }}
                className="text-xs bg-blue-400 hover:bg-blue-500 text-white px-3 py-1 rounded transition flex-1"
              >
                ✏️ Notitie
              </button>
              <button
                onClick={() => speak(card.swedish)}
                disabled={playing}
                className="text-xs bg-blue-400 hover:bg-blue-500 text-white px-3 py-1 rounded transition flex-1 disabled:opacity-50"
              >
                🔊 Hoor
              </button>
            </div>
          </div>

          {editingNotes && (
            <div className="w-full max-w-sm bg-white rounded-lg shadow-lg p-4 mb-8">
              <input
                type="text"
                value={notesInput}
                onChange={(e) => setNotesInput(e.target.value)}
                placeholder="bijv. possessief, werkwoord, archaic..."
                className="w-full px-3 py-2 border border-gray-300 rounded mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSaveNotes}
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded transition text-sm min-h-10"
                >
                  💾 Opslaan
                </button>
                <button
                  onClick={() => setEditingNotes(false)}
                  className="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded transition text-sm min-h-10"
                >
                  Sluiten
                </button>
              </div>
            </div>
          )}

          <div className="mb-8" />

          {flipped && (
            <div className="flex gap-4 w-full max-w-sm">
              <button
                onClick={() => handleAnswer(false)}
                className="flex-1 bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg transition transform hover:scale-105 text-lg min-h-12"
              >
                ❌ Fout
              </button>
              <button
                onClick={() => handleAnswer(true)}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg transition transform hover:scale-105 text-lg min-h-12"
              >
                ✅ Goed
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
