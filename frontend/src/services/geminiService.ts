import { ChatMessage } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function getChatResponse(history: ChatMessage[], message: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

    const data = await response.json();
    return data.text || "Xin lỗi, tôi gặp trục trặc. Thử lại nhé!";

  } catch (error) {
    console.error("Chat Error:", error);
    return "Xin lỗi, hiện tại tôi không thể trả lời. Vui lòng thử lại sau.";
  }
}