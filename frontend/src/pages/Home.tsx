import React from "react";
import { Link } from "react-router-dom";

export function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-5xl font-bold text-blue-900 mb-4">Svenska Lären</h1>
        <p className="text-xl text-blue-800 mb-12">
          Leer Zweeds met interactieve oefeningen powered door AI.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Link
            to="/flashcard"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105"
          >
            <div className="text-4xl mb-4">🗂️</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">Flitskaarten</h2>
            <p className="text-gray-700 text-sm">
              Leer woordenschat met spaced repetition (Leitner-dozen systeem).
            </p>
          </Link>

          <Link
            to="/translation"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105"
          >
            <div className="text-4xl mb-4">🔄</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">Vertalen</h2>
            <p className="text-gray-700 text-sm">
              Vertaal zinnen tussen Nederlands en Zweeds, krijg feedback.
            </p>
          </Link>

          <Link
            to="/conversation"
            className="bg-white shadow-lg rounded-lg p-8 hover:shadow-xl transition transform hover:scale-105 sm:col-span-2 sm:max-w-xs sm:mx-auto"
          >
            <div className="text-4xl mb-4">💬</div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">Conversatie</h2>
            <p className="text-gray-700 text-sm">
              Oefen gratis conversatie met een AI Zweedse gesprekspartner.
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
