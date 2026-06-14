import React from "react";
import { Link } from "react-router-dom";
import { DifficultySlider } from "./DifficultySlider";

export function NavBar() {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center gap-4">
        <Link to="/" className="text-2xl font-bold">
          Svenska Lären
        </Link>
        <div className="flex items-center gap-6 w-full max-w-xs">
          <span className="text-sm font-semibold">Moeilijkheid:</span>
          <DifficultySlider />
        </div>
      </div>
    </nav>
  );
}
