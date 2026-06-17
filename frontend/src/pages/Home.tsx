import React, { useState } from "react";
import { Link } from "react-router-dom";

export function Home() {
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");

  const handleSyncWordlist = async () => {
    setSyncing(true);
    try {
      const res = await fetch("/api/cards/sync/wordlist", { method: "POST" });
      const data = await res.json();
      setSyncMessage(
        `✅ ${data.added} woorden toegevoegd! Totaal: ${data.total_words}`,
      );
    } catch (error) {
      setSyncMessage("❌ Synchronisatie mislukt");
    }
    setSyncing(false);
    setTimeout(() => setSyncMessage(""), 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-5xl font-bold text-blue-900 mb-4">Svenska Lären</h1>
        <p className="text-xl text-blue-800 mb-8">
          Leer Zweeds met interactieve oefeningen powered door AI.
        </p>

        <div className="mb-8">
          <button
            onClick={handleSyncWordlist}
            disabled={syncing}
            className="text-sm bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition disabled:opacity-50 min-h-10"
          >
            {syncing ? "Synchroniseren..." : "📚 Meer woorden laden"}
          </button>
          {syncMessage && (
            <p className="text-sm text-gray-700 mt-2">{syncMessage}</p>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Link
            to="/flashcard"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105"
          >
            <div className="text-4xl mb-4">🗂️</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">
              Flitskaarten
            </h2>
            <p className="text-gray-700 text-sm">
              Leer woordenschat met spaced repetition.
            </p>
          </Link>

          <Link
            to="/translation"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105"
          >
            <div className="text-4xl mb-4">↔️</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">Vertalen</h2>
            <p className="text-gray-700 text-sm">
              Vertaal zinnen van Zweeds naar Nederlands en omgekeerd.
            </p>
          </Link>

          <Link
            to="/conversation"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105"
          >
            <div className="text-4xl mb-4">💬</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">
              Conversatie
            </h2>
            <p className="text-gray-700 text-sm">
              Oefen conversatie met een AI Zweedse gesprekspartner.
            </p>
          </Link>

          <Link
            to="/woordenlijst"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105"
          >
            <div className="text-4xl mb-4">📖</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">
              Woordenlijst
            </h2>
            <p className="text-gray-700 text-sm">
              Doorzoek woorden, beluister uitspraak, voeg notities toe.
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
