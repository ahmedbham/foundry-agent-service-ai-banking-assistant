import { useCallback, useState } from "react";
import MessageList, { type Message } from "./components/MessageList";
import ChatInput from "./components/ChatInput";
import { sendMessage } from "./services/api";

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const handleSend = useCallback(
    async (text: string) => {
      const userMsg: Message = { role: "user", content: text };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);

      // Add empty assistant message that will be filled by deltas
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      try {
        await sendMessage(
          text,
          conversationId,
          (delta) => {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = {
                ...last,
                content: last.content + delta,
              };
              return updated;
            });
          },
          (newConversationId) => {
            setConversationId(newConversationId);
          }
        );
      } catch {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: "Sorry, something went wrong. Please try again.",
          };
          return updated;
        });
      } finally {
        setIsStreaming(false);
      }
    },
    [conversationId]
  );

  return (
    <div className="app">
      <header className="app-header">
        <h1>Banking Assistant</h1>
      </header>
      <MessageList messages={messages} isStreaming={isStreaming} />
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
