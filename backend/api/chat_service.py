import re
from google import genai
from django.conf import settings
from django.db import models as db_models
from .models import Books, FAQ, Categories, Authors, Review, OrderItems

_GEMINI_SYSTEM = (
    'Bạn là trợ lý của Remix Bookstore — một cửa hàng sách trực tuyến tại Việt Nam. '
    'Hãy trả lời ngắn gọn, thân thiện bằng tiếng Việt. '
    'Nếu câu hỏi liên quan đến sách, văn học, tác giả hoặc chủ đề đọc sách thì hãy tư vấn nhiệt tình. '
    'Nếu câu hỏi hoàn toàn không liên quan đến sách, hãy lịch sự chuyển hướng về chủ đề sách.'
)


def _ask_gemini(user_message: str) -> str:
    """Gọi Gemini để trả lời câu hỏi ngoài lề. Trả về chuỗi text, hoặc '' nếu lỗi."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return ''
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f'{_GEMINI_SYSTEM}\n\nKhách hỏi: {user_message}',
        )
        return response.text.strip()
    except Exception as e:
        print(f'Gemini error: {e}')
        return ''


STOP_WORDS = {
    'có', 'sách', 'không', 'nào', 'của', 'tôi', 'muốn', 'tìm', 'xem',
    'giới', 'thiệu', 'cho', 'với', 'và', 'hoặc', 'là', 'được', 'bán',
    'mua', 'cần', 'ơi', 'ạ', 'nhé', 'thế', 'này', 'đó', 'thì', 'mà',
}


def _clean_query(message: str) -> str:
    words = message.split()
    return ' '.join(w for w in words if w.lower() not in STOP_WORDS and len(w) >= 2)


def _books_to_data(books, extras: dict = None) -> list:
    result = []
    for b in books:
        item = {
            'id': b.book_id,
            'title': b.title,
            'author': b.author.full_name if b.author else 'Đang cập nhật',
            'price': float(b.price),
            'image_url': b.image_url or None,
            'stock': b.stock_quantity,
        }
        if extras and b.book_id in extras:
            item.update(extras[b.book_id])
        result.append(item)
    return result


def _qs(model):
    return model.objects.select_related('author', 'category')


def _search_faq(message: str):
    words = [w for w in message.lower().split() if len(w) >= 3]
    for word in words:
        faq = FAQ.objects.filter(question__icontains=word, is_active=True).first()
        if faq:
            return faq.answer
    return None


def _search_books_by_title(query: str):
    books = _qs(Books).filter(title__icontains=query)[:5]
    if books.exists():
        return list(books)
    for word in (w for w in query.split() if len(w) >= 2):
        books = _qs(Books).filter(title__icontains=word)[:5]
        if books.exists():
            return list(books)
    return []


# ── intent handlers ──────────────────────────────────────────────────────────

def _reply_greet():
    return {
        'text': (
            'Chào anh/chị! Em là trợ lý của Remix Bookstore 😊\n'
            'Em có thể giúp anh/chị:\n'
            '• Tìm sách theo tên, thể loại, tác giả\n'
            '• Sách giá cao nhất / rẻ nhất\n'
            '• Sách được đánh giá tốt nhất\n'
            '• Sách bán chạy nhất\n'
            '• Sách sắp hết hàng\n'
            '• Trả lời câu hỏi về đơn hàng, vận chuyển\n\n'
            'Anh/chị cần gì ạ?'
        ),
        'books': [],
    }


def _reply_most_expensive():
    books = _qs(Books).order_by('-price')[:5]
    return {'text': 'Dạ, đây là Top 5 cuốn sách có giá cao nhất hiện tại:', 'books': _books_to_data(books)}


def _reply_cheapest():
    books = _qs(Books).order_by('price')[:5]
    return {'text': 'Dạ, đây là Top 5 cuốn sách có giá thấp nhất:', 'books': _books_to_data(books)}


def _reply_top_rated():
    top = (
        Review.objects
        .values('book_id')
        .annotate(avg=db_models.Avg('rating'), cnt=db_models.Count('id'))
        .filter(cnt__gte=1)
        .order_by('-avg', '-cnt')[:5]
    )
    if not top:
        return {'text': 'Hiện chưa có đánh giá nào trên hệ thống. Anh/chị hãy là người đầu tiên nhé!', 'books': []}
    book_ids = [r['book_id'] for r in top]
    extras = {r['book_id']: {'avg_rating': round(r['avg'], 1)} for r in top}
    books = sorted(_qs(Books).filter(book_id__in=book_ids), key=lambda b: book_ids.index(b.book_id))
    return {'text': 'Dạ, đây là Top 5 cuốn sách được đánh giá cao nhất:', 'books': _books_to_data(books, extras)}


def _reply_best_sellers():
    top = (
        OrderItems.objects
        .values('book_id')
        .annotate(total_sold=db_models.Sum('quantity'))
        .order_by('-total_sold')[:5]
    )
    if not top:
        books = _qs(Books).all()[:5]
        return {'text': 'Hiện chưa có dữ liệu đơn hàng. Anh/chị xem sách gợi ý nhé!', 'books': _books_to_data(books)}
    book_ids = [r['book_id'] for r in top]
    extras = {r['book_id']: {'sold': r['total_sold']} for r in top}
    books = sorted(_qs(Books).filter(book_id__in=book_ids), key=lambda b: book_ids.index(b.book_id))
    return {'text': 'Dạ, đây là Top 5 cuốn sách bán chạy nhất:', 'books': _books_to_data(books, extras)}


def _reply_low_stock():
    books = _qs(Books).filter(stock_quantity__gt=0, stock_quantity__lte=10).order_by('stock_quantity')[:5]
    if books.exists():
        return {'text': 'Dạ, đây là các cuốn sách sắp hết hàng (còn dưới 10 cuốn):', 'books': _books_to_data(books)}
    return {'text': 'Hiện tại không có sách nào sắp hết hàng. Kho hàng còn đủ anh/chị nhé!', 'books': []}


def _reply_high_stock():
    books = _qs(Books).order_by('-stock_quantity')[:5]
    return {'text': 'Dạ, đây là Top 5 cuốn sách còn nhiều hàng nhất:', 'books': _books_to_data(books)}


def _reply_price_under(msg: str):
    match = re.search(r'(\d+)\s*(?:k|nghìn|ngàn|đồng|vnd)?', msg)
    if not match:
        return None
    raw = int(match.group(1))
    price = raw * 1000 if raw <= 1000 else raw
    books = _qs(Books).filter(price__lte=price).order_by('-price')[:5]
    if books.exists():
        label = f'{raw}k' if raw <= 1000 else f'{raw}đ'
        return {'text': f'Dạ, đây là sách có giá dưới {label}:', 'books': _books_to_data(books)}
    return {'text': 'Không tìm thấy sách nào dưới mức giá đó. Anh/chị thử tầm giá khác nhé!', 'books': []}


def _reply_by_author(msg: str):
    for author in Authors.objects.all():
        name_lower = author.full_name.lower()
        parts = [p for p in name_lower.split() if len(p) >= 3]
        if name_lower in msg or any(p in msg for p in parts):
            books = _qs(Books).filter(author=author)[:5]
            if books.exists():
                return {'text': f'Dạ, đây là sách của tác giả "{author.full_name}":', 'books': _books_to_data(books)}
    return None


def _reply_by_category(msg: str):
    for cat in Categories.objects.all():
        if cat.name.lower() in msg:
            books = _qs(Books).filter(category=cat)[:5]
            if books.exists():
                return {'text': f'Dạ, đây là sách thuộc thể loại "{cat.name}":', 'books': _books_to_data(books)}
    return None


def _reply_fallback():
    books = _qs(Books).all()[:5]
    return {
        'text': (
            'Dạ, em chưa tìm thấy kết quả phù hợp. '
            'Anh/chị có thể hỏi về:\n'
            '• Sách theo tên / tác giả / thể loại\n'
            '• Sách đánh giá tốt nhất / bán chạy nhất\n'
            '• Sách giá rẻ nhất / giá cao nhất\n'
            '• Sách sắp hết hàng\n\n'
            'Đây là một số sách gợi ý:'
        ),
        'books': _books_to_data(books),
    }


# ── intent detection ──────────────────────────────────────────────────────────

INTENTS = [
    (['xin chào', 'hello', 'chào', 'hi', 'hey', 'alo'], 'greet', 'startswith'),
    (['mắc nhất', 'đắt nhất', 'giá cao nhất', 'giá mắc nhất'], 'expensive', 'contains'),
    (['rẻ nhất', 'giá rẻ nhất', 'thấp nhất', 'giá rẻ'], 'cheap', 'contains'),
    (['đánh giá tốt', 'đánh giá cao', 'được đánh giá', 'review tốt',
      'rating cao', 'nhiều sao', 'được yêu thích', 'yêu thích nhất',
      'tốt nhất', 'hay nhất', 'đánh giá nhiều', 'nhiều đánh giá'], 'top_rated', 'contains'),
    (['bán chạy', 'bán nhiều', 'phổ biến nhất', 'hot nhất',
      'nhiều người mua', 'được mua nhiều', 'bestseller', 'best seller'], 'best_sellers', 'contains'),
    (['sắp hết', 'sắp hết hàng', 'còn ít', 'gần hết', 'hàng ít'], 'low_stock', 'contains'),
    (['còn nhiều', 'còn hàng nhiều', 'nhiều hàng', 'hàng nhiều'], 'high_stock', 'contains'),
    (['dưới', 'tầm', 'khoảng'], 'price_under', 'contains'),
]


def _detect_intent(msg: str) -> str | None:
    for keywords, intent, mode in INTENTS:
        if mode == 'startswith':
            if any(msg == w or msg.startswith(w) for w in keywords):
                return intent
        else:
            if any(w in msg for w in keywords):
                return intent
    return None


# ── main entry point ──────────────────────────────────────────────────────────

_SIMPLE_HANDLERS = {
    'greet': _reply_greet,
    'expensive': _reply_most_expensive,
    'cheap': _reply_cheapest,
    'top_rated': _reply_top_rated,
    'best_sellers': _reply_best_sellers,
    'low_stock': _reply_low_stock,
    'high_stock': _reply_high_stock,
}

_QUESTION_SIGNALS = [
    '?', 'nên', 'thế nào', 'làm sao', 'tại sao', 'vì sao',
    'như thế', 'có nên', 'bao giờ', 'khi nào', 'để giảm',
    'để tăng', 'để học', 'để đọc', 'gợi ý', 'tư vấn',
    'khác nhau', 'so sánh', 'ý nghĩa', 'chủ đề',
]


def _is_question(msg: str) -> bool:
    return any(w in msg for w in _QUESTION_SIGNALS)


def _contextual_lookup(msg: str, raw: str):
    """Chain: author → category (bỏ qua nếu là câu hỏi) → FAQ."""
    result = _reply_by_author(msg)
    if result:
        return result

    # Bỏ qua category nếu câu có dấu hiệu hỏi (vd: "khác nhau giữa tiểu thuyết...")
    if not _is_question(msg):
        result = _reply_by_category(msg)
        if result:
            return result

    faq = _search_faq(raw)
    if faq:
        return {'text': f'Dạ, em xin trả lời:\n\n{faq}', 'books': []}

    return None


def _title_search(raw: str):
    """Tìm sách theo từ khóa trong tên — chỉ dùng khi Gemini không trả lời được."""
    clean = _clean_query(raw)
    if not clean:
        return None
    found = _search_books_by_title(clean)
    if found:
        label = f'Dạ, em tìm thấy {len(found)} cuốn sách phù hợp:' if len(found) > 1 else 'Dạ, em tìm thấy cuốn sách này:'
        return {'text': label, 'books': _books_to_data(found)}
    return None


def get_chat_reply(user_message: str) -> dict:
    """Trả về dict: { 'text': str, 'books': list }"""
    try:
        msg = user_message.lower().strip()
        intent = _detect_intent(msg)

        handler = _SIMPLE_HANDLERS.get(intent)
        if handler:
            return handler()

        if intent == 'price_under':
            result = _reply_price_under(msg)
            if result:
                return result

        # author / category / FAQ
        result = _contextual_lookup(msg, user_message)
        if result:
            return result

        if _is_question(msg):
            # Câu hỏi / tư vấn → Gemini, không fallback về tìm sách
            gemini_text = _ask_gemini(user_message)
            if gemini_text:
                return {'text': gemini_text, 'books': []}
            return {
                'text': (
                    'Dạ, em chưa có đủ thông tin để trả lời câu này.\n'
                    'Anh/chị thử hỏi về:\n'
                    '• Tên sách / tác giả / thể loại\n'
                    '• Sách đánh giá tốt nhất, bán chạy nhất\n'
                    '• Sách giá rẻ nhất, sắp hết hàng'
                ),
                'books': [],
            }
        else:
            # Tìm kiếm → title search trước, Gemini nếu không thấy sách
            result = _title_search(user_message)
            if result:
                return result
            gemini_text = _ask_gemini(user_message)
            if gemini_text:
                return {'text': gemini_text, 'books': []}
            return _reply_fallback()

    except Exception as e:
        print(f"Chat Service Error: {e}")
        return {
            'text': 'Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau ít phút nhé!',
            'books': [],
        }
