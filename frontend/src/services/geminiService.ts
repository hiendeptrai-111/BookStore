import { ChatMessage } from "../types";
import { apiFetch } from "./api";

export async function getChatResponse(
  history: ChatMessage[],
  message: string,
): Promise<string> {
  try {
    // Convert chat history to format expected by backend
    const formattedHistory = history.map((msg) => ({
      role: msg.role === "user" ? "user" : "model",
      text: msg.text,
    }));

    const response = await apiFetch("/chat/", {
      method: "POST",
      body: JSON.stringify({
        message,
        history: formattedHistory,
      }),
    });

    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

    const data = await response.json();
    return data.text || "Xin lỗi, tôi gặp trục trặc. Thử lại nhé!";
  } catch (error) {
    console.error("Chat Error:", error);
    return "Xin lỗi, hiện tại tôi không thể trả lời. Vui lòng thử lại sau.";
  }
}
