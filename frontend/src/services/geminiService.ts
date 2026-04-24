import { ChatMessage, ChatBookCard } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface ChatResponse {
  text: string;
  books: ChatBookCard[];
}

export async function getChatResponse(history: ChatMessage[], message: string): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

    const data = await response.json();
    return {
      text: data.text || "Xin lỗi, tôi gặp trục trặc. Thử lại nhé!",
      books: data.books || [],
    };

  } catch (error) {
    console.error("Chat Error:", error);
    return {
      text: "Xin lỗi, hiện tại tôi không thể trả lời. Vui lòng thử lại sau.",
      books: [],
    };
  }
}
