import { useState } from "react";
import { searchCards, updateCardNotes } from "../api";
import { useTTS } from "../hooks/useTTS";
import type { WordCard } from "../api";

interface SearchResult extends WordCard {
  direction: string;
}

export function Woordenlijst() {
  const { speak, playing } = useTTS();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingNotes, setEditingNotes] = useState("");

  const handleSearch = async (q: string) => {
    setQuery(q);
    if (q.trim().length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const found = await searchCards(q);
      setResults(found);
    } catch (error) {
      console.error("Search failed:", error);
    }
    setLoading(false);
  };

  const handleSaveNotes = async (cardId: number) => {
    try {
      await updateCardNotes(cardId, editingNotes);
      setResults(
        results.map((card) =>
          card.id === cardId ? { ...card, notes: editingNotes || undefined } : card
        )
      );
      setEditingId(null);
      setEditingNotes("");
    } catch (error) {
      console.error("Failed to save notes:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-purple-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-purple-900 mb-8">Woordenlijst</h1>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Zoek woorden (bijv. 'har' zoekt ook 'hår' en 'här')..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
          />
          {query.length > 0 && query.length < 2 && (
            <p className="text-sm text-gray-500 mt-2">Minimaal 2 karakters</p>
          )}
        </div>

        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-600">Zoeken...</p>
          </div>
        )}

        {!loading && results.length === 0 && query.length >= 2 && (
          <div className="text-center py-12">
            <p className="text-gray-600">Geen resultaten gevonden</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-purple-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-purple-900">
                      Zweeds
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-purple-900">
                      Nederlands
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-purple-900">
                      Richting
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-purple-900">
                      Acties
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.map((card) => (
                    <tr key={`${card.id}-${card.direction}`} className="hover:bg-purple-50">
                      <td className="px-6 py-4 text-gray-800">{card.swedish}</td>
                      <td className="px-6 py-4 text-gray-800">{card.dutch}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {card.direction === "se_nl" ? "SE→NL" : "NL→SE"}
                      </td>
                      <td className="px-6 py-4 space-x-2">
                        <button
                          onClick={() => speak(card.swedish)}
                          disabled={playing}
                          className="text-sm bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded transition disabled:opacity-50"
                        >
                          🔊
                        </button>
                        <button
                          onClick={() => {
                            setEditingId(card.id);
                            setEditingNotes(card.notes || "");
                          }}
                          className="text-sm bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded transition"
                        >
                          ✏️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {editingId !== null && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">Notities bewerken</h2>
              <input
                type="text"
                value={editingNotes}
                onChange={(e) => setEditingNotes(e.target.value)}
                placeholder="bijv. possessief, werkwoord, archaic..."
                className="w-full px-3 py-2 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => handleSaveNotes(editingId)}
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded transition font-semibold"
                >
                  💾 Opslaan
                </button>
                <button
                  onClick={() => setEditingId(null)}
                  className="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded transition font-semibold"
                >
                  Sluiten
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
