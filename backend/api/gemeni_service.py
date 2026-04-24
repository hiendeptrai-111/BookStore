import google.generativeai as genai
from django.conf import settings
from .models import FAQ, Book  # import model Book của bạn

# Cấu hình Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def get_faq_context():
    """Lấy toàn bộ FAQ từ DB để đưa vào context."""
    faqs = FAQ.objects.filter(is_active=True)
    if not faqs.exists():
        return ""
    
    faq_text = "=== BỘ CÂU HỎI THƯỜNG GẶP ===\n"
    for faq in faqs:
        faq_text += f"Q: {faq.question}\nA: {faq.answer}\n\n"
    return faq_text


def get_books_context(query: str = ""):
    """Lấy danh sách sách từ DB, có thể filter theo query."""
    # Tuỳ chỉnh theo model Book của bạn
    if query:
        books = Book.objects.filter(
            title__icontains=query
        ) | Book.objects.filter(
            author__icontains=query
        ) | Book.objects.filter(
            category__icontains=query
        )
    else:
        books = Book.objects.all()[:20]  # Giới hạn 20 cuốn để tránh quá dài
    
    if not books.exists():
        return ""
    
    books_text = "=== DANH SÁCH SÁCH TRONG CỬA HÀNG ===\n"
    for book in books:
        books_text += (
            f"- Tên: {book.title} | Tác giả: {book.author} "
            f"| Giá: {book.price}đ | Thể loại: {book.category}\n"
        )
    return books_text


def chat_with_gemini(user_message: str, chat_history: list = None) -> str:
    """
    Gửi tin nhắn đến Gemini kèm context từ DB.
    chat_history: [{"role": "user/model", "parts": ["..."]}]
    """
    try:
        # Xây dựng system prompt với dữ liệu từ DB
        faq_context = get_faq_context()
        books_context = get_books_context(query=user_message)
        
        system_prompt = f"""Bạn là trợ lý AI của cửa hàng sách Remix Bookstore.
Nhiệm vụ của bạn:
1. Tư vấn sách phù hợp cho khách hàng
2. Trả lời các câu hỏi về đơn hàng, vận chuyển, thanh toán
3. Luôn thân thiện, nhiệt tình bằng tiếng Việt

{faq_context}

{books_context}

Lưu ý:
- Chỉ trả lời dựa trên thông tin có sẵn ở trên
- Nếu không có thông tin, hãy nói "Tôi chưa có thông tin về vấn đề này, bạn vui lòng liên hệ hotline để được hỗ trợ"
- Không bịa đặt thông tin về giá, tác giả, hay chính sách
"""
        
        # Khởi tạo chat với history (cho phép hội thoại nhiều lượt)
        history = chat_history or []
        chat = model.start_chat(history=history)
        
        # Gửi message kèm system prompt (lần đầu)
        if not history:
            full_message = f"{system_prompt}\n\nKhách hàng hỏi: {user_message}"
        else:
            full_message = user_message
        
        response = chat.send_message(full_message)
        return response.text
        
    except Exception as e:
        return f"Xin lỗi, có lỗi xảy ra: {str(e)}"