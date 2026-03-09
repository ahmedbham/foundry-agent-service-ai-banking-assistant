import { useEffect, useRef } from "react";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  messages: Message[];
  isStreaming: boolean;
}

export default function MessageList({ messages, isStreaming }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  return (
    <div className="message-list">
      {messages.length === 0 && (
        <div className="empty-state">
          <h2>Banking Assistant</h2>
          <p>Ask me about your account balance, credit information, or payment methods.</p>
        </div>
      )}
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          <div className="message-bubble">
            {msg.content}
            {msg.role === "assistant" && isStreaming && i === messages.length - 1 && (
              <span className="cursor" />
            )}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
