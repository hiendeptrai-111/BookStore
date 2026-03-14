import { GoogleGenAI } from "@google/genai";
import { ChatMessage } from "../types";
import.meta.env

const ai = new GoogleGenAI({ 
  apiKey: import.meta.env.VITE_GEMINI_API_KEY 
});
console.log(import.meta.env.VITE_GEMINI_API_KEY);
export async function getChatResponse(history: ChatMessage[], message: string) {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: [
        ...history.map(msg => ({
          role: msg.role,
          parts: [{ text: msg.text }]
        })),
        {
          role: "user",
          parts: [{ text: message }]
        }
      ],
      config: {
        systemInstruction: "Bạn là một trợ lý ảo thân thiện của BookStore - Nhà Sách Trực Tuyến. Hãy trả lời các câu hỏi của khách hàng về sách, đơn hàng và các dịch vụ của cửa hàng một cách chuyên nghiệp và nhiệt tình. Nếu khách hàng hỏi về những thứ không liên quan đến sách hoặc cửa hàng, hãy khéo léo dẫn dắt họ quay lại chủ đề chính.",
      }
    });

    return response.text || "Xin lỗi, tôi gặp chút trục trặc. Bạn có thể thử lại sau không?";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "Xin lỗi, hiện tại tôi không thể trả lời. Vui lòng kiểm tra kết nối mạng hoặc thử lại sau.";
  }
}
