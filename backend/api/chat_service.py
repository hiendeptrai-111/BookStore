from .models import Books, FAQ, Categories, Authors


STOP_WORDS = {
    'có', 'sách', 'không', 'nào', 'của', 'tôi', 'muốn', 'tìm', 'xem',
    'giới', 'thiệu', 'cho', 'với', 'và', 'hoặc', 'là', 'được', 'bán',
    'mua', 'cần', 'ơi', 'ạ', 'nhé', 'thế', 'này', 'đó', 'thì', 'mà',
}


def _clean_query(message: str) -> str:
    """Lọc stop words để lấy từ khóa tìm kiếm."""
    words = message.split()
    filtered = [w for w in words if w.lower() not in STOP_WORDS and len(w) >= 2]
    return ' '.join(filtered)


def _books_to_data(books) -> list:
    result = []
    for b in books:
        result.append({
            'id': b.book_id,
            'title': b.title,
            'author': b.author.full_name if b.author else 'Đang cập nhật',
            'price': float(b.price),
            'image_url': b.image_url or None,
            'stock': b.stock_quantity,
        })
    return result


def _search_faq(message: str):
    try:
        words = [w for w in message.lower().split() if len(w) >= 3]
        for word in words:
            faq = FAQ.objects.filter(question__icontains=word, is_active=True).first()
            if faq:
                return faq.answer
        return None
    except Exception:
        return None


def _search_books_by_title(query: str):
    """Tìm sách theo nhiều từ khóa, trả về kết quả tốt nhất."""
    # Thử tìm với toàn bộ query trước
    books = Books.objects.select_related('author', 'category').filter(
        title__icontains=query
    )[:5]
    if books.exists():
        return list(books)

    # Tìm từng từ một, lấy kết quả nhiều nhất
    words = [w for w in query.split() if len(w) >= 2]
    for word in words:
        books = Books.objects.select_related('author', 'category').filter(
            title__icontains=word
        )[:5]
        if books.exists():
            return list(books)

    return []


def get_chat_reply(user_message: str) -> dict:
    """Trả về dict: { 'text': str, 'books': list }"""
    try:
        msg = user_message.lower().strip()

        # 1. Chào hỏi
        greet_words = ['xin chào', 'hello', 'chào', 'hi', 'hey', 'alo']
        if any(msg == w or msg.startswith(w) for w in greet_words):
            return {
                'text': (
                    'Chào anh/chị! Em là trợ lý của Remix Bookstore 😊\n'
                    'Em có thể giúp anh/chị:\n'
                    '• Tìm sách theo tên, thể loại, tác giả\n'
                    '• Xem sách mắc nhất / rẻ nhất\n'
                    '• Trả lời câu hỏi về đơn hàng, vận chuyển\n\n'
                    'Anh/chị cần gì ạ?'
                ),
                'books': [],
            }

        # 2. Sách mắc nhất / đắt nhất
        if any(w in msg for w in ['mắc nhất', 'đắt nhất', 'giá cao nhất', 'cao nhất', 'giá mắc nhất']):
            books = Books.objects.select_related('author', 'category').order_by('-price')[:5]
            return {
                'text': 'Dạ, đây là Top 5 cuốn sách có giá cao nhất hiện tại:',
                'books': _books_to_data(books),
            }

        # 3. Sách rẻ nhất
        if any(w in msg for w in ['rẻ nhất', 'giá rẻ nhất', 'thấp nhất', 'giá rẻ', 'rẻ nhất']):
            books = Books.objects.select_related('author', 'category').order_by('price')[:5]
            return {
                'text': 'Dạ, đây là Top 5 cuốn sách có giá thấp nhất:',
                'books': _books_to_data(books),
            }

        # 4. Tìm theo tác giả
        try:
            authors = Authors.objects.all()
            for author in authors:
                name_lower = author.full_name.lower()
                if name_lower in msg or any(part in msg for part in name_lower.split() if len(part) >= 3):
                    books = Books.objects.select_related('author', 'category').filter(
                        author=author
                    )[:5]
                    if books.exists():
                        return {
                            'text': f'Dạ, đây là sách của tác giả "{author.full_name}":',
                            'books': _books_to_data(books),
                        }
        except Exception:
            pass

        # 5. Tìm theo thể loại
        try:
            categories = Categories.objects.all()
            for cat in categories:
                if cat.name.lower() in msg:
                    books = Books.objects.select_related('author', 'category').filter(
                        category=cat
                    )[:5]
                    if books.exists():
                        return {
                            'text': f'Dạ, đây là sách thuộc thể loại "{cat.name}":',
                            'books': _books_to_data(books),
                        }
        except Exception:
            pass

        # 6. Tìm trong FAQ
        faq_answer = _search_faq(user_message)
        if faq_answer:
            return {'text': f'Dạ, em xin trả lời:\n\n{faq_answer}', 'books': []}

        # 7. Tìm theo tên sách (dùng query đã lọc stop words)
        clean = _clean_query(user_message)
        if clean:
            found = _search_books_by_title(clean)
            if found:
                count = len(found)
                label = f'Dạ, em tìm thấy {count} cuốn sách phù hợp:' if count > 1 else 'Dạ, em tìm thấy cuốn sách này:'
                return {'text': label, 'books': _books_to_data(found)}

        # 8. Fallback — gợi ý sách nổi bật
        books = list(Books.objects.select_related('author', 'category').all()[:5])
        return {
            'text': 'Dạ, em chưa tìm thấy kết quả phù hợp. Đây là một số sách gợi ý của cửa hàng:',
            'books': _books_to_data(books),
        }

    except Exception as e:
        print(f"Chat Service Error: {str(e)}")
        return {
            'text': 'Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau ít phút nhé!',
            'books': [],
        }
