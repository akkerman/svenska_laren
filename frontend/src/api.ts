const API_BASE = "/api";

export interface Settings {
  difficulty: number;
}

export interface WordCard {
  id: number;
  swedish: string;
  dutch: string;
  notes?: string;
  box: number;
  next_review: string | null;
  total_correct: number;
  total_wrong: number;
}

export interface BoxCount {
  filtered: number;
  total: number;
}

export interface CardStats {
  total: number;
  mastered: number;
  per_box: BoxCount[];
}

export interface TranslationResponse {
  sentence: string;
  language_from: string;
  language_to: string;
  correct_translation: string;
}

export interface EvaluationResponse {
  source_sentence: string;
  user_attempt: string;
  correct_translation: string;
  feedback: string;
}

export interface ConversationStartResponse {
  session_id: string;
  opening_message: string;
}

// Settings
export async function getSettings(): Promise<Settings> {
  const res = await fetch(`${API_BASE}/settings`);
  return res.json();
}

export async function updateSettings(difficulty: number): Promise<Settings> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ difficulty }),
  });
  return res.json();
}

// Vocabulary
export async function getDueCards(direction: string = "se_nl"): Promise<WordCard[]> {
  const res = await fetch(`${API_BASE}/cards/due?direction=${direction}`);
  return res.json();
}

export async function getStats(direction: string = "se_nl"): Promise<CardStats> {
  const res = await fetch(`${API_BASE}/cards/stats?direction=${direction}`);
  return res.json();
}

export async function answerCard(
  card_id: number,
  correct: boolean
): Promise<{ new_box: number; next_review: string | null }> {
  const res = await fetch(`${API_BASE}/cards/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ card_id, correct }),
  });
  return res.json();
}

export async function addCustomWord(
  swedish: string,
  dutch: string
): Promise<WordCard> {
  const res = await fetch(`${API_BASE}/cards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ swedish, dutch }),
  });
  return res.json();
}

export async function searchCards(query: string, direction: string = "se_nl"): Promise<WordCard[]> {
  const res = await fetch(
    `${API_BASE}/cards/search?q=${encodeURIComponent(query)}&direction=${direction}`
  );
  return res.json();
}

export async function updateCardNotes(card_id: number, notes: string): Promise<{ status: string; notes: string | null }> {
  const res = await fetch(`${API_BASE}/cards/${card_id}/notes?notes=${encodeURIComponent(notes)}`, {
    method: "PATCH",
  });
  return res.json();
}

// Translation
export async function generateTranslation(
  direction: string,
  difficulty: number,
  topic?: string,
  exclude_sentence?: string
): Promise<TranslationResponse> {
  const res = await fetch(`${API_BASE}/translation/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ direction, topic, difficulty, exclude_sentence }),
  });
  return res.json();
}

export async function evaluateTranslation(
  source_sentence: string,
  user_attempt: string,
  direction: string,
  difficulty: number,
  correct_translation: string
): Promise<EvaluationResponse> {
  const res = await fetch(`${API_BASE}/translation/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_sentence, user_attempt, direction, difficulty, correct_translation }),
  });
  return res.json();
}

// Conversation
export async function startConversation(
  topic: string,
  difficulty: number
): Promise<ConversationStartResponse> {
  const res = await fetch(`${API_BASE}/conversation/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, difficulty }),
  });
  return res.json();
}

export async function* streamConversationMessage(
  session_id: string,
  user_message: string,
  difficulty: number
): AsyncGenerator<string> {
  const res = await fetch(`${API_BASE}/conversation/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, user_message, difficulty }),
  });

  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.token) yield data.token;
        } catch (e) {
          // ignore parse errors
        }
      }
    }
  }
}

export async function getConversationHistory(session_id: string) {
  const res = await fetch(`${API_BASE}/conversation/history/${session_id}`);
  return res.json();
}

export async function deleteConversation(session_id: string) {
  const res = await fetch(`${API_BASE}/conversation/${session_id}`, {
    method: "DELETE",
  });
  return res.json();
}
