# backend/api/chat_service.py
# File riêng xử lý toàn bộ logic chatbot - không dùng AI bên ngoài

from django.db import models as django_models
from .models import Books, Authors, Categories, Orders, Customers


# ============================================================
#  KEYWORD PATTERNS - Thêm từ khóa tại đây để mở rộng
# ============================================================

PATTERNS = {
    'greeting':     ['xin chào', 'chào', 'hello', 'hi', 'hey', 'alo', 'good morning', 'good evening'],
    'thanks':       ['cảm ơn', 'thank', 'thanks', 'cám ơn', 'tuyệt', 'hay quá', 'ok', 'được rồi'],
    'goodbye':      ['tạm biệt', 'bye', 'goodbye', 'hẹn gặp lại', 'thôi nhé'],
    'help':         ['giúp', 'hướng dẫn', 'help', 'hỗ trợ', 'tôi cần', 'làm sao', 'như thế nào', 'có thể'],

    'all_books':    ['tất cả', 'danh sách sách', 'có sách gì', 'có những sách', 'liệt kê', 'toàn bộ sách', 'show all'],
    'new_books':    ['mới nhất', 'sách mới', 'vừa ra', 'mới về', 'mới cập nhật', 'mới thêm'],
    'cheap_books':  ['rẻ nhất', 'giá rẻ', 'giá thấp', 'tiết kiệm', 'ít tiền', 'rẻ', 'bình dân'],
    'expensive_books': ['đắt nhất', 'giá cao', 'cao cấp', 'premium', 'đắt'],
    'in_stock':     ['còn hàng', 'còn không', 'có sẵn', 'in stock', 'còn bán', 'đang có'],
    'out_stock':    ['hết hàng', 'out of stock', 'hết rồi', 'không còn'],
    'bestseller':   ['bán chạy', 'best seller', 'phổ biến', 'nhiều người mua', 'hot', 'nổi tiếng'],

    'category':     ['thể loại', 'loại sách', 'chủ đề', 'category', 'genre', 'dạng sách', 'mảng'],
    'author':       ['tác giả', 'author', 'viết bởi', 'ai viết', 'người viết'],
    'price':        ['giá', 'bao nhiêu tiền', 'price', 'cost', 'phí', 'giá bán', 'giá tiền'],
    'search':       ['tìm', 'search', 'tìm kiếm', 'có không', 'bán không', 'có cuốn', 'có sách'],

    'recommend':    ['gợi ý', 'recommend', 'đề xuất', 'nên đọc', 'hay nhất', 'tốt nhất', 'nên mua', 'tư vấn'],
    'kids':         ['thiếu nhi', 'trẻ em', 'cho bé', 'cho trẻ', 'children', 'kids'],
    'novel':        ['tiểu thuyết', 'truyện dài', 'novel', 'fiction'],
    'comic':        ['truyện tranh', 'manga', 'comic', 'truyện hình'],
    'science':      ['khoa học', 'science', 'stem', 'kỹ thuật', 'công nghệ'],
    'history':      ['lịch sử', 'history', 'cổ đại', 'chiến tranh'],
    'skill':        ['kỹ năng', 'skill', 'self-help', 'phát triển bản thân', 'học kỹ năng'],
    'cooking':      ['nấu ăn', 'cookbook', 'ẩm thực', 'công thức'],

    'store_info':   ['cửa hàng', 'thông tin', 'giờ mở cửa', 'địa chỉ', 'liên hệ', 'hotline', 'store'],
    'order':        ['đặt hàng', 'mua', 'order', 'thanh toán', 'checkout', 'giỏ hàng', 'cart'],
    'shipping':     ['giao hàng', 'ship', 'vận chuyển', 'delivery', 'nhận hàng', 'phí ship'],
    'return':       ['đổi trả', 'return', 'hoàn tiền', 'refund', 'trả hàng', 'bảo hành'],
    'discount':     ['giảm giá', 'khuyến mãi', 'discount', 'sale', 'voucher', 'coupon', 'ưu đãi'],
}


def _match(message: str, pattern_keys: list) -> bool:
    """Kiểm tra message có chứa từ khóa nào không."""
    return any(
        kw in message
        for key in pattern_keys
        for kw in PATTERNS.get(key, [])
    )


def _format_book(b, show_desc=False) -> str:
    stock = f"{b.stock_quantity} cuốn" if b.stock_quantity > 0 else "⚠️ Hết hàng"
    text = (
        f"📖 *{b.title}*\n"
        f"   👤 Tác giả: {b.author.full_name}\n"
        f"   🏷️ Thể loại: {b.category.name}\n"
        f"   💰 Giá: {b.price:,.0f}đ\n"
        f"   📦 Tồn kho: {stock}"
    )
    if show_desc and b.description:
        text += f"\n   📝 {b.description[:100]}..."
    return text


def _search_books(keyword: str):
    """Tìm sách theo từ khóa trong tên, tác giả, thể loại, mô tả."""
    return Books.objects.select_related('author', 'category').filter(
        django_models.Q(title__icontains=keyword) |
        django_models.Q(author__full_name__icontains=keyword) |
        django_models.Q(category__name__icontains=keyword) |
        django_models.Q(description__icontains=keyword)
    )


def _extract_search_keyword(message: str) -> str:
    """Lấy từ khóa tìm kiếm từ câu hỏi."""
    remove_words = [
        'tìm', 'search', 'có', 'không', 'bán', 'cuốn', 'sách',
        'cho tôi', 'giúp tôi', 'tôi muốn', 'tôi cần', 'mua',
        'tìm kiếm', 'xem', 'xem thử', 'có không', 'bán không'
    ]
    result = message
    for w in remove_words:
        result = result.replace(w, '').strip()
    return result.strip()


# ============================================================
#  HÀM CHÍNH - Xử lý câu hỏi
# ============================================================

def get_chat_reply(message: str) -> str:
    msg = message.strip().lower()
    books_qs = Books.objects.select_related('author', 'category')

    # ----------------------------------------------------------
    # 1. CHÀO HỎI
    # ----------------------------------------------------------
    if _match(msg, ['greeting']):
        total = books_qs.count()
        in_stock = books_qs.filter(stock_quantity__gt=0).count()
        return (
            f"Xin chào! 👋 Chào mừng đến với BookStore!\n\n"
            f"📚 Hiện có *{total}* đầu sách, *{in_stock}* cuốn đang có sẵn.\n\n"
            f"Tôi có thể giúp bạn:\n"
            f"• 🔍 Tìm sách theo tên, tác giả, thể loại\n"
            f"• 💰 Xem sách giá rẻ / đắt nhất\n"
            f"• 🆕 Xem sách mới nhất\n"
            f"• 📦 Kiểm tra tình trạng hàng\n"
            f"• 🎯 Gợi ý sách theo sở thích\n"
            f"• ℹ️ Thông tin đặt hàng, giao hàng, đổi trả\n\n"
            f"Bạn cần tìm gì? 😊"
        )

    # ----------------------------------------------------------
    # 2. CẢM ƠN / TẠM BIỆT
    # ----------------------------------------------------------
    if _match(msg, ['thanks']):
        return "Không có gì! 😊 Nếu cần thêm gì cứ hỏi tôi nhé!"

    if _match(msg, ['goodbye']):
        return "Tạm biệt! 👋 Cảm ơn bạn đã ghé BookStore. Hẹn gặp lại nhé!"

    # ----------------------------------------------------------
    # 3. HƯỚNG DẪN
    # ----------------------------------------------------------
    if _match(msg, ['help']):
        return (
            "Tôi có thể giúp bạn:\n\n"
            "🔍 *Tìm sách:* Nhập tên sách, tác giả hoặc thể loại\n"
            "   VD: 'Doraemon', 'Nguyễn Nhật Ánh', 'thiếu nhi'\n\n"
            "💰 *Giá:* 'sách rẻ nhất', 'sách đắt nhất'\n\n"
            "🆕 *Mới:* 'sách mới nhất', 'mới về'\n\n"
            "📦 *Tồn kho:* 'còn hàng không', 'hết hàng'\n\n"
            "🎯 *Gợi ý:* 'gợi ý sách thiếu nhi', 'tư vấn sách kỹ năng'\n\n"
            "🏷️ *Thể loại:* 'danh sách thể loại'\n\n"
            "👤 *Tác giả:* 'danh sách tác giả'\n\n"
            "🛒 *Mua hàng:* 'cách đặt hàng', 'phí ship', 'đổi trả'"
        )

    # ----------------------------------------------------------
    # 4. THÔNG TIN CỬA HÀNG
    # ----------------------------------------------------------
    if _match(msg, ['store_info']):
        return (
            "ℹ️ *Thông tin BookStore:*\n\n"
            "🏪 Cửa hàng sách trực tuyến\n"
            "🌐 Website: localhost:5173\n"
            "📞 Hotline: 1800-BOOK (hỗ trợ 8:00 - 22:00)\n"
            "📧 Email: support@bookstore.vn\n\n"
            f"📚 Hiện có {books_qs.count()} đầu sách đang bán"
        )

    if _match(msg, ['order']):
        return (
            "🛒 *Cách đặt hàng:*\n\n"
            "1. Tìm sách bạn muốn mua\n"
            "2. Nhấn *Thêm vào giỏ hàng*\n"
            "3. Vào *Giỏ hàng* → kiểm tra đơn\n"
            "4. Nhấn *Thanh toán* → điền địa chỉ\n"
            "5. Xác nhận đơn hàng\n\n"
            "Đơn hàng sẽ được xử lý trong vòng 24 giờ! ✅"
        )

    if _match(msg, ['shipping']):
        return (
            "🚚 *Thông tin giao hàng:*\n\n"
            "• Giao hàng toàn quốc\n"
            "• Phí ship: 25.000đ - 40.000đ tùy khu vực\n"
            "• *Miễn phí ship* cho đơn từ 300.000đ\n"
            "• Thời gian: 2-5 ngày làm việc\n"
            "• Nội thành: 1-2 ngày\n\n"
            "📦 Đơn hàng được đóng gói cẩn thận!"
        )

    if _match(msg, ['return']):
        return (
            "🔄 *Chính sách đổi trả:*\n\n"
            "✅ Đổi trả trong vòng *7 ngày* kể từ ngày nhận\n"
            "✅ Sách còn nguyên vẹn, chưa qua sử dụng\n"
            "✅ Có hóa đơn mua hàng\n\n"
            "❌ Không áp dụng với sách đã qua sử dụng\n\n"
            "📞 Liên hệ hotline để được hỗ trợ đổi trả!"
        )

    if _match(msg, ['discount']):
        return (
            "🏷️ *Khuyến mãi & Ưu đãi:*\n\n"
            "• Giảm 10% cho đơn đầu tiên\n"
            "• Miễn phí ship cho đơn từ 300.000đ\n"
            "• Ưu đãi thành viên thân thiết\n"
            "• Flash sale vào cuối tuần\n\n"
            "💡 Theo dõi website để cập nhật khuyến mãi mới nhất!"
        )

    # ----------------------------------------------------------
    # 5. DANH SÁCH SÁCH
    # ----------------------------------------------------------
    if _match(msg, ['all_books']):
        all_books = books_qs.filter(stock_quantity__gt=0)[:10]
        total = books_qs.count()
        lines = [f"📖 {b.title} — {b.author.full_name} — {b.price:,.0f}đ" for b in all_books]
        text = f"📚 Cửa hàng có *{total}* đầu sách. Đây là một số sách đang có hàng:\n\n" + "\n".join(lines)
        if total > 10:
            text += f"\n\n👉 Còn {total - 10} cuốn khác. Tìm theo tên, tác giả hoặc thể loại để xem chi tiết!"
        return text

    if _match(msg, ['new_books']):
        new_books = books_qs.order_by('-book_id')[:5]
        lines = [_format_book(b) for b in new_books]
        return "🆕 *Sách mới nhất tại cửa hàng:*\n\n" + "\n\n".join(lines)

    if _match(msg, ['cheap_books']):
        cheap = books_qs.filter(stock_quantity__gt=0).order_by('price')[:5]
        lines = [_format_book(b) for b in cheap]
        return "💰 *Sách giá rẻ nhất:*\n\n" + "\n\n".join(lines)

    if _match(msg, ['expensive_books']):
        expensive = books_qs.filter(stock_quantity__gt=0).order_by('-price')[:5]
        lines = [_format_book(b) for b in expensive]
        return "💎 *Sách cao cấp nhất:*\n\n" + "\n\n".join(lines)

    if _match(msg, ['in_stock']):
        count = books_qs.filter(stock_quantity__gt=0).count()
        return f"✅ Hiện tại có *{count}* đầu sách đang còn hàng.\n\nBạn muốn tìm loại sách nào?"

    if _match(msg, ['out_stock']):
        count = books_qs.filter(stock_quantity=0).count()
        return f"⚠️ Hiện có *{count}* đầu sách đã hết hàng.\n\nBạn có thể tìm sách tương tự đang còn hàng nhé!"

    if _match(msg, ['bestseller']):
        # Lấy sách có trong nhiều đơn hàng nhất
        from .models import OrderItems
        from django.db.models import Count
        top_books = (
            OrderItems.objects.values('book')
            .annotate(total_sold=Count('id'))
            .order_by('-total_sold')[:5]
        )
        book_ids = [item['book'] for item in top_books]
        if book_ids:
            top = books_qs.filter(book_id__in=book_ids)
            lines = [_format_book(b) for b in top]
            return "🔥 *Sách bán chạy nhất:*\n\n" + "\n\n".join(lines)
        else:
            popular = books_qs.filter(stock_quantity__gt=0)[:5]
            lines = [_format_book(b) for b in popular]
            return "🔥 *Sách nổi bật:*\n\n" + "\n\n".join(lines)

    # ----------------------------------------------------------
    # 6. DANH MỤC / TÁC GIẢ
    # ----------------------------------------------------------
    if _match(msg, ['category']) and _match(msg, ['all_books', 'category']) or 'danh sách thể loại' in msg or 'các thể loại' in msg:
        cats = Categories.objects.all()
        lines = []
        for c in cats:
            count = books_qs.filter(category=c, stock_quantity__gt=0).count()
            lines.append(f"• {c.name} ({count} cuốn còn hàng)")
        return "🏷️ *Các thể loại sách:*\n\n" + "\n".join(lines) + "\n\n👉 Gõ tên thể loại để xem sách!"

    if _match(msg, ['author']) and ('danh sách' in msg or 'tất cả' in msg or 'các tác giả' in msg):
        authors = Authors.objects.all()
        lines = []
        for a in authors:
            count = books_qs.filter(author=a).count()
            lines.append(f"• {a.full_name} ({count} cuốn)")
        return "👤 *Các tác giả:*\n\n" + "\n".join(lines) + "\n\n👉 Gõ tên tác giả để xem sách của họ!"

    # ----------------------------------------------------------
    # 7. GỢI Ý THEO THỂ LOẠI
    # ----------------------------------------------------------
    genre_map = {
        'kids':      ('thiếu nhi', '👶'),
        'novel':     ('tiểu thuyết', '📕'),
        'comic':     ('truyện tranh', '🎨'),
        'science':   ('khoa học', '🔬'),
        'history':   ('lịch sử', '🏛️'),
        'skill':     ('kỹ năng', '💡'),
        'cooking':   ('nấu ăn', '🍳'),
    }

    for key, (genre_kw, emoji) in genre_map.items():
        if _match(msg, [key]) or _match(msg, ['recommend']) and genre_kw in msg:
            matched = books_qs.filter(
                django_models.Q(category__name__icontains=genre_kw) |
                django_models.Q(description__icontains=genre_kw)
            ).filter(stock_quantity__gt=0)[:5]
            if matched.exists():
                lines = [_format_book(b) for b in matched]
                return f"{emoji} *Gợi ý sách {genre_kw}:*\n\n" + "\n\n".join(lines)
            else:
                return f"Hiện chưa có sách {genre_kw} trong kho. Bạn thử tìm thể loại khác nhé!"

    if _match(msg, ['recommend']):
        random_books = books_qs.filter(stock_quantity__gt=0).order_by('?')[:3]
        lines = [_format_book(b, show_desc=True) for b in random_books]
        return "🎯 *Gợi ý sách cho bạn:*\n\n" + "\n\n".join(lines) + "\n\n👉 Cho tôi biết thể loại bạn thích để gợi ý chính xác hơn!"

    # ----------------------------------------------------------
    # 8. HỎI GIÁ / TÌM KIẾM CỤ THỂ
    # ----------------------------------------------------------
    # Hỏi giá khoảng bao nhiêu
    if 'dưới' in msg and ('đồng' in msg or 'k' in msg or '000' in msg):
        try:
            import re
            nums = re.findall(r'\d+', msg)
            if nums:
                max_price = int(nums[0])
                if max_price < 1000:
                    max_price *= 1000  # 100k → 100000
                cheap = books_qs.filter(price__lte=max_price, stock_quantity__gt=0).order_by('price')[:5]
                if cheap.exists():
                    lines = [_format_book(b) for b in cheap]
                    return f"💰 *Sách giá dưới {max_price:,.0f}đ:*\n\n" + "\n\n".join(lines)
                else:
                    return f"Không tìm thấy sách giá dưới {max_price:,.0f}đ. Bạn thử tăng mức giá lên nhé!"
        except:
            pass

    # ----------------------------------------------------------
    # 9. TÌM KIẾM TỰ DO (fallback thông minh)
    # ----------------------------------------------------------
    # Thử tìm trực tiếp với toàn bộ message
    direct_search = _search_books(msg)
    if direct_search.exists():
        results = direct_search[:5]
        lines = [_format_book(b) for b in results]
        total = direct_search.count()
        header = f"🔍 Tìm thấy *{total}* kết quả cho '{message}':\n\n"
        text = header + "\n\n".join(lines)
        if total > 5:
            text += f"\n\n👉 Còn {total - 5} kết quả khác. Hãy thu hẹp từ khóa tìm kiếm!"
        return text

    # Thử tìm với từ khóa đã lọc
    keyword = _extract_search_keyword(msg)
    if keyword and len(keyword) >= 2:
        keyword_search = _search_books(keyword)
        if keyword_search.exists():
            results = keyword_search[:5]
            lines = [_format_book(b) for b in results]
            return f"🔍 *Kết quả tìm '{keyword}':*\n\n" + "\n\n".join(lines)

    # ----------------------------------------------------------
    # 10. KHÔNG HIỂU - GỢI Ý THÔNG MINH
    # ----------------------------------------------------------
    # Đoán xem user có thể muốn hỏi gì
    suggestions = []
    if any(c.isdigit() for c in msg):
        suggestions.append("💰 Bạn muốn tìm sách theo giá? Thử: 'sách dưới 100k'")
    if len(msg) >= 3:
        suggestions.append(f"🔍 Thử tìm: '{msg}' → không có kết quả")

    return (
        f"Xin lỗi, tôi chưa hiểu câu hỏi này 😅\n\n"
        f"Bạn có thể thử:\n"
        f"• 🔍 Tìm theo *tên sách* (vd: 'Harry Potter')\n"
        f"• 👤 Tìm theo *tác giả* (vd: 'Nguyễn Nhật Ánh')\n"
        f"• 🏷️ Tìm theo *thể loại* (vd: 'thiếu nhi', 'tiểu thuyết')\n"
        f"• 💰 Tìm theo *giá* (vd: 'sách dưới 100k', 'sách rẻ nhất')\n"
        f"• 🆕 'Sách mới nhất'\n"
        f"• 🔥 'Sách bán chạy'\n"
        f"• ❓ 'Hướng dẫn' để xem thêm\n"
    )