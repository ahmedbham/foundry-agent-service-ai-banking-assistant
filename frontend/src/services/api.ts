const API_BASE = import.meta.env.VITE_API_URL || "";

export interface ChatEvent {
  type: "delta" | "done";
  content?: string;
  conversation_id?: string;
}

export async function sendMessage(
  message: string,
  conversationId: string | null,
  onDelta: (text: string) => void,
  onDone: (conversationId: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

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
      if (!line.startsWith("data: ")) continue;
      const json = line.slice(6).trim();
      if (!json) continue;

      const event: ChatEvent = JSON.parse(json);
      if (event.type === "delta" && event.content) {
        onDelta(event.content);
      } else if (event.type === "done") {
        onDone(event.conversation_id || "");
      }
    }
  }
}
