import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SettingsProvider } from "./context/SettingsContext";
import { NavBar } from "./components/NavBar";
import { Home } from "./pages/Home";
import { Flashcard } from "./pages/Flashcard";
import { Translation } from "./pages/Translation";
import { Conversation } from "./pages/Conversation";
import "./index.css";

function App() {
  return (
    <SettingsProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <NavBar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/flashcard" element={<Flashcard />} />
            <Route path="/translation" element={<Translation />} />
            <Route path="/conversation" element={<Conversation />} />
          </Routes>
        </div>
      </BrowserRouter>
    </SettingsProvider>
  );
}

export default App;
