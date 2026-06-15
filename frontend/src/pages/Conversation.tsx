import { useState, useRef, useEffect } from "react";
import {
  startConversation,
  streamConversationMessage,
  deleteConversation,
} from "../api";
import { useSettings } from "../context/SettingsContext";
import { SwedishChars } from "../components/SwedishChars";
import { MarkdownText } from "../components/MarkdownText";
import { useTTS } from "../hooks/useTTS";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function Conversation() {
  const { difficulty } = useSettings();
  const { speak, playing } = useTTS();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [topic, setTopic] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleCharClick = (char: string) => {
    setUserInput(userInput + char);
    inputRef.current?.focus();
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleStartConversation = async () => {
    if (!topic.trim()) return;

    setLoading(true);
    try {
      const result = await startConversation(topic, difficulty);
      setSessionId(result.session_id);
      setMessages([
        {
          role: "assistant",
          content: result.opening_message,
        },
      ]);
      setTopic(topic);
    } catch (error) {
      console.error("Failed to start conversation:", error);
    }
    setLoading(false);
  };

  const handleSendMessage = async () => {
    if (!userInput.trim() || !sessionId) return;

    const userMessage = userInput;
    setUserInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    setStreaming(true);
    try {
      let assistantMessage = "";

      for await (const chunk of streamConversationMessage(
        sessionId,
        userMessage,
        difficulty
      )) {
        assistantMessage += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          if (
            updated.length > 0 &&
            updated[updated.length - 1].role === "assistant"
          ) {
            updated[updated.length - 1].content = assistantMessage;
          } else {
            updated.push({ role: "assistant", content: assistantMessage });
          }
          return updated;
        });
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    }
    setStreaming(false);
  };

  const handleReset = async () => {
    if (sessionId) {
      try {
        await deleteConversation(sessionId);
      } catch (error) {
        console.error("Failed to delete conversation:", error);
      }
    }
    setSessionId(null);
    setMessages([]);
    setTopic("");
    setUserInput("");
  };

  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-purple-50 to-purple-100 py-8 px-4 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-purple-900 mb-4">
            Conversatie
          </h1>
          <p className="text-gray-600 mb-6">
            Kies een onderwerp en chat met je Zweedse gesprekspartner!
          </p>

          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="bijv. eten, reizen, familie, hobby's"
            onKeyDown={(e) => e.key === "Enter" && handleStartConversation()}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            onClick={handleStartConversation}
            disabled={loading || !topic.trim()}
            className="w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 rounded-lg transition disabled:opacity-50 min-h-12"
          >
            {loading ? "Starten..." : "Conversatie starten"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-purple-100 flex flex-col">
      <div className="max-w-2xl w-full mx-auto flex-1 flex flex-col p-4">
        <div className="mb-4 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-purple-900">
            Onderwerp: {topic}
          </h1>
          <button
            onClick={handleReset}
            className="text-sm bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition min-h-10"
          >
            Opnieuw
          </button>
        </div>

        <div className="flex-1 bg-white rounded-lg shadow-lg p-6 mb-4 overflow-y-auto">
          {messages.map((msg, idx) => (
            <div key={idx} className="mb-4">
              <p className="text-sm font-semibold text-gray-600 mb-1">
                {msg.role === "user" ? "Jij" : "Partner"}
              </p>
              <div
                className={`p-3 rounded-lg ${
                  msg.role === "user"
                    ? "bg-purple-100 text-purple-900"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                <div className="text-sm leading-relaxed">
                  {msg.role === "assistant" ? (
                    <MarkdownText content={msg.content} />
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  )}
                </div>
                {msg.role === "assistant" && (
                  <button
                    onClick={() => speak(msg.content)}
                    disabled={playing}
                    className="text-xs bg-purple-500 hover:bg-purple-600 text-white px-2 py-1 rounded transition disabled:opacity-50 mt-2"
                  >
                    🔊 Luister
                  </button>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div>
          <SwedishChars onCharClick={handleCharClick} />
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !streaming && handleSendMessage()
              }
              placeholder="Typ je bericht in het Zweeds of Nederlands..."
              disabled={streaming}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
            />
            <button
              onClick={handleSendMessage}
              disabled={streaming || !userInput.trim()}
              className="bg-purple-500 hover:bg-purple-600 text-white font-bold px-6 py-2 rounded-lg transition disabled:opacity-50 min-h-10"
            >
              Verzend
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
