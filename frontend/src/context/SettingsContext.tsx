import React, { createContext, useContext, useState, useEffect } from "react";
import { getSettings, updateSettings } from "../api";

interface SettingsContextType {
  difficulty: number;
  setDifficulty: (value: number) => void;
  loading: boolean;
}

const SettingsContext = createContext<SettingsContextType | undefined>(
  undefined
);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [difficulty, setDifficultyState] = useState(0.3);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSettings().then((data) => {
      setDifficultyState(data.difficulty);
      setLoading(false);
    });
  }, []);

  const setDifficulty = (value: number) => {
    setDifficultyState(value);
    updateSettings(value);
  };

  return (
    <SettingsContext.Provider value={{ difficulty, setDifficulty, loading }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within SettingsProvider");
  }
  return context;
}
