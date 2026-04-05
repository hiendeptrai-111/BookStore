import json
import os
import re
import unicodedata

from django.db.models import Q, Sum

from .chat_service import get_chat_reply
from .models import Authors, Books, Categories, Orders, OrderItems

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - handled at runtime
    genai = None


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and genai:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
else:
    model = None


BOOK_FIELDS = ("author", "category", "publisher")
GREETING_KEYWORDS = ("xin chao", "chao", "hello", "hi", "hey", "alo")
THANKS_KEYWORDS = ("cam on", "thanks", "thank", "ok", "duoc roi", "tuyet")
GOODBYE_KEYWORDS = ("tam biet", "bye", "goodbye", "hen gap lai", "thoi nhe")
HELP_KEYWORDS = ("giup", "huong dan", "help", "ho tro", "tu van")
ORDER_KEYWORDS = (
    "don hang",
    "don dat hang",
    "dat hang",
    "order",
    "thanh toan",
    "gio hang",
    "checkout",
    "da mua",
    "mua",
)
USER_ORDER_KEYWORDS = (
    "don hang cua toi",
    "don dat hang cua toi",
    "don cua toi",
    "kiem tra don hang",
    "kiem tra don dat hang",
    "kiem tra cac don",
    "trang thai don hang",
    "lich su don hang",
    "toi da dat",
    "toi da dat hang",
    "toi da mua",
    "lich su mua",
    "don gan day",
    "mua gi",
)
SELF_REFERENCE_KEYWORDS = ("toi", "cua toi", "minh", "toi da")
SHIPPING_KEYWORDS = ("giao hang", "ship", "van chuyen", "delivery", "phi ship")
RETURN_KEYWORDS = ("doi tra", "hoan tien", "refund", "bao hanh", "tra hang")
DISCOUNT_KEYWORDS = ("giam gia", "khuyen mai", "discount", "sale", "voucher", "coupon", "uu dai")
STATS_KEYWORDS = ("thong ke", "doanh thu", "tong don", "tong sach", "so don", "bao cao")
CHEAPEST_KEYWORDS = ("re nhat", "gia re", "gia thap", "tiet kiem", "binh dan")
EXPENSIVE_KEYWORDS = ("dat nhat", "gia cao", "cao cap", "premium")
NEWEST_KEYWORDS = ("moi nhat", "sach moi", "moi ve", "vua ra", "moi them")
BESTSELLER_KEYWORDS = ("ban chay", "best seller", "bestseller", "pho bien", "hot", "noi bat")
ALL_BOOKS_KEYWORDS = ("tat ca", "danh sach sach", "co sach gi", "liet ke", "toan bo sach")
CATEGORY_LIST_KEYWORDS = ("the loai", "danh muc", "category", "genre")
AUTHOR_LIST_KEYWORDS = ("tac gia", "author", "nguoi viet", "viet boi")
LIST_INTENT_KEYWORDS = ("danh sach", "tat ca", "liet ke", "co nhung", "cac")
PRICE_FILTER_KEYWORDS = ("duoi", "toi da", "khong qua", "under", "price", "gia")
STOPWORDS = {
    "ai",
    "anh",
    "ban",
    "bao",
    "bao_nhieu",
    "bi",
    "bo",
    "boi",
    "cac",
    "cho",
    "co",
    "con",
    "cua",
    "cuon",
    "dang",
    "duoc",
    "don",
    "dat",
    "gi",
    "gia",
    "giu",
    "giup",
    "hang",
    "hay",
    "khong",
    "kiem",
    "la",
    "lam",
    "liet",
    "loai",
    "mau",
    "moi",
    "mot",
    "nay",
    "nao",
    "ne",
    "nhieu",
    "nhat",
    "nhung",
    "nua",
    "o",
    "phan",
    "sach",
    "ship",
    "so",
    "ten",
    "the",
    "the_loai",
    "theo",
    "tim",
    "tim_kiem",
    "toi",
    "tra",
    "tren",
    "tro",
    "tu",
    "tu_van",
    "va",
    "ve",
    "vui",
    "voi",
    "xem",
}
STORE_POLICIES = {
    "order": [
        "Chọn sách và nhấn 'Thêm vào giỏ hàng'.",
        "Mở giỏ hàng, kiểm tra số lượng rồi nhấn 'Thanh toán'.",
        "Điền địa chỉ, số điện thoại và xác nhận đơn.",
        "Đơn sẽ được xử lý trong vòng 24 giờ.",
    ],
    "shipping": {
        "nationwide": True,
        "fee": "25,000đ - 40,000đ",
        "free_shipping_threshold": 300000,
        "estimated_time": "2-5 ngày làm việc",
        "same_day_in_ha_noi": True,
    },
    "return": {
        "period": "7 ngày",
        "condition": "Sách còn nguyên vẹn, chưa qua sử dụng",
        "support": "Liên hệ hotline để được hỗ trợ đổi trả",
    },
    "discount": [
        "Giảm 10% cho đơn đầu tiên.",
        "Miễn phí ship cho đơn từ 300,000đ.",
        "Flash sale cuối tuần và ưu đãi thành viên.",
    ],
}
CONTACT_INFO = {
    "store_name": "BookStore",
    "website": "http://localhost:5173",
    "email": "support@bookstore.vn",
    "phone": "1800-BOOK",
}
PRICE_LIMIT_PATTERN = re.compile(
    r"(?:duoi|toi da|khong qua|under)\s*(\d+(?:[.,]\d+)?)\s*(k|ngan|nghin|tr|trieu)?"
)
TOKEN_PATTERN = re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+")
QUOTE_PATTERN = re.compile(r'"([^"]+)"|“([^”]+)”|\'([^\']+)\'')


def check_gemini_api_key():
    """Kiểm tra API key khi thực sự cần dùng."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY chưa được cấu hình.")
    return True


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", (text or "").replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _normalize_text(text: str) -> str:
    normalized = _strip_accents((text or "").lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _contains_any(message: str, keywords: tuple[str, ...]) -> bool:
    for keyword in keywords:
        pattern = r"(?<![a-z0-9])" + re.escape(keyword).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        if re.search(pattern, message):
            return True
    return False


def _is_personal_order_request(message: str) -> bool:
    if _contains_any(message, USER_ORDER_KEYWORDS):
        return True

    has_order_phrase = _contains_any(
        message,
        ("don hang", "don dat hang", "dat hang", "trang thai don", "lich su don"),
    )
    has_self_reference = _contains_any(message, SELF_REFERENCE_KEYWORDS)
    return has_order_phrase and has_self_reference


def _dedupe(values):
    result = []
    seen = set()
    for value in values:
        key = value.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(value.strip())
    return result


def _format_currency(value) -> str:
    numeric = float(value or 0)
    return f"{numeric:,.0f}đ"


def _format_stock(stock_quantity: int) -> str:
    if stock_quantity <= 0:
        return "Hết hàng"
    return f"Còn {stock_quantity} cuốn"


def _serialize_book(book: Books, include_description: bool = False, total_sold=None) -> dict:
    payload = {
        "id": book.book_id,
        "title": book.title,
        "author": book.author.full_name if book.author else None,
        "category": book.category.name if book.category else None,
        "publisher": book.publisher.name if book.publisher else None,
        "price": float(book.price),
        "stock": book.stock_quantity,
        "isbn": book.isbn,
    }
    if include_description and book.description:
        payload["description"] = book.description[:240]
    if total_sold is not None:
        payload["total_sold"] = int(total_sold)
    return payload


def _serialize_category(category: Categories, book_count: int) -> dict:
    return {
        "id": category.category_id,
        "name": category.name,
        "book_count": book_count,
    }


def _serialize_author(author: Authors, book_count: int) -> dict:
    return {
        "id": author.author_id,
        "name": author.full_name,
        "nationality": author.nationality,
        "book_count": book_count,
    }


def _build_history_transcript(chat_history: list | None, limit: int = 6) -> str:
    if not chat_history:
        return "Chưa có lịch sử hội thoại."

    transcript = []
    for item in chat_history[-limit:]:
        role = "Khách hàng" if item.get("role") == "user" else "Trợ lý"
        text = str(item.get("text", "")).strip()
        if text:
            transcript.append(f"{role}: {text}")
    return "\n".join(transcript) if transcript else "Chưa có lịch sử hội thoại."


def _extract_terms_from_text(text: str) -> list[str]:
    if not text:
        return []

    terms = []
    for groups in QUOTE_PATTERN.findall(text):
        phrase = next((value for value in groups if value), "").strip()
        if phrase:
            terms.append(phrase)

    for token in TOKEN_PATTERN.findall(text.lower()):
        normalized = _normalize_text(token)
        if len(normalized) < 2 or normalized in STOPWORDS or token.isdigit():
            continue
        terms.append(token)

    return _dedupe(terms)


def _extract_search_terms(message: str, chat_history: list | None = None) -> list[str]:
    terms = _extract_terms_from_text(message)
    if len(terms) >= 2 or not chat_history:
        return terms[:6]

    for item in reversed(chat_history):
        if item.get("role") != "user":
            continue
        terms.extend(_extract_terms_from_text(str(item.get("text", ""))))
        if len(terms) >= 6:
            break

    return _dedupe(terms)[:6]


def _extract_price_limit(message: str) -> int | None:
    normalized = _normalize_text(message)
    match = PRICE_LIMIT_PATTERN.search(normalized)
    if not match:
        return None

    raw_number = match.group(1).replace(",", ".")
    if raw_number.count(".") > 1:
        raw_number = raw_number.replace(".", "")

    try:
        amount = float(raw_number)
    except ValueError:
        return None

    unit = match.group(2)
    if unit in {"k", "ngan", "nghin"}:
        amount *= 1000
    elif unit in {"tr", "trieu"}:
        amount *= 1_000_000

    return int(amount)


def _search_books_by_terms(terms: list[str], limit: int = 5) -> list[Books]:
    if not terms:
        return []

    queryset = Books.objects.select_related(*BOOK_FIELDS)
    query = Q()
    for term in terms:
        query |= (
            Q(title__icontains=term)
            | Q(author__full_name__icontains=term)
            | Q(category__name__icontains=term)
            | Q(publisher__name__icontains=term)
            | Q(description__icontains=term)
            | Q(isbn__icontains=term)
        )

    direct_matches = list(queryset.filter(query).distinct()[:limit])
    if direct_matches:
        return direct_matches

    normalized_terms = [_normalize_text(term) for term in terms if term]
    ranked = []
    for book in queryset.all():
        haystack = _normalize_text(
            " ".join(
                [
                    book.title,
                    book.author.full_name if book.author else "",
                    book.category.name if book.category else "",
                    book.publisher.name if book.publisher else "",
                    book.description or "",
                    book.isbn or "",
                ]
            )
        )
        score = sum(1 for term in normalized_terms if term and term in haystack)
        if score:
            ranked.append((score, int(book.stock_quantity > 0), book.book_id, book))

    ranked.sort(key=lambda item: (-item[0], -item[1], -item[2]))
    return [item[3] for item in ranked[:limit]]


def _search_categories_by_terms(terms: list[str], limit: int = 6) -> list[dict]:
    if not terms:
        return []

    categories = []
    for category in Categories.objects.all():
        haystack = _normalize_text(category.name)
        score = sum(1 for term in terms if _normalize_text(term) in haystack)
        if score:
            book_count = Books.objects.filter(category=category).count()
            categories.append((score, category.category_id, _serialize_category(category, book_count)))

    categories.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in categories[:limit]]


def _search_authors_by_terms(terms: list[str], limit: int = 6) -> list[dict]:
    if not terms:
        return []

    authors = []
    for author in Authors.objects.all():
        haystack = _normalize_text(" ".join([author.full_name, author.nationality or ""]))
        score = sum(1 for term in terms if _normalize_text(term) in haystack)
        if score:
            book_count = Books.objects.filter(author=author).count()
            authors.append((score, author.author_id, _serialize_author(author, book_count)))

    authors.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in authors[:limit]]


def _get_bestseller_books(limit: int = 5) -> list[dict]:
    top_sales = list(
        OrderItems.objects.values("book")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")[:limit]
    )
    if not top_sales:
        return []

    books = Books.objects.select_related(*BOOK_FIELDS).filter(
        book_id__in=[item["book"] for item in top_sales]
    )
    book_map = {book.book_id: book for book in books}
    results = []
    for item in top_sales:
        book = book_map.get(item["book"])
        if not book:
            continue
        results.append(_serialize_book(book, include_description=True, total_sold=item["total_sold"] or 0))
    return results


def _get_store_overview() -> dict:
    revenue = Orders.objects.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or 0
    return {
        "store_name": CONTACT_INFO["store_name"],
        "total_books": Books.objects.count(),
        "in_stock_books": Books.objects.filter(stock_quantity__gt=0).count(),
        "total_categories": Categories.objects.count(),
        "total_authors": Authors.objects.count(),
        "total_orders": Orders.objects.count(),
        "revenue": float(revenue),
        "contact": CONTACT_INFO,
    }


def _get_store_stats() -> dict:
    recent_orders = Orders.objects.select_related("customer").order_by("-order_date")[:5]
    revenue = Orders.objects.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or 0
    return {
        "books": Books.objects.count(),
        "in_stock": Books.objects.filter(stock_quantity__gt=0).count(),
        "out_of_stock": Books.objects.filter(stock_quantity__lte=0).count(),
        "orders": Orders.objects.count(),
        "revenue": float(revenue),
        "recent_orders": [
            {
                "order_id": order.order_id,
                "customer_name": order.customer.full_name if order.customer else None,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "order_date": str(order.order_date),
            }
            for order in recent_orders
        ],
    }


def _get_user_order_context(user_id: int, limit: int = 3) -> dict | None:
    orders = list(
        Orders.objects.filter(customer_id=user_id)
        .select_related("customer")
        .order_by("-order_date")[:limit]
    )
    if not orders:
        return None

    total_spent = (
        Orders.objects.filter(customer_id=user_id)
        .exclude(status="cancelled")
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    serialized_orders = []
    for order in orders:
        items = OrderItems.objects.filter(order=order).select_related("book")[:5]
        serialized_orders.append(
            {
                "order_id": order.order_id,
                "status": order.status,
                "order_date": str(order.order_date),
                "total_amount": float(order.total_amount),
                "address": order.address,
                "phone": order.phone,
                "items": [
                    {
                        "title": item.book.title if item.book else None,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                    }
                    for item in items
                ],
            }
        )

    return {
        "order_count": Orders.objects.filter(customer_id=user_id).count(),
        "total_spent": float(total_spent),
        "recent_orders": serialized_orders,
    }


def build_runtime_context(message: str, chat_history: list | None = None, user_id: int | None = None) -> dict:
    normalized_message = _normalize_text(message)
    personal_order_request = _is_personal_order_request(normalized_message)
    search_terms = [] if personal_order_request else _extract_search_terms(message, chat_history)
    price_limit = _extract_price_limit(message)
    wants_category_listing = _contains_any(normalized_message, CATEGORY_LIST_KEYWORDS) and (
        _contains_any(normalized_message, LIST_INTENT_KEYWORDS) or normalized_message in CATEGORY_LIST_KEYWORDS
    )
    wants_author_listing = _contains_any(normalized_message, AUTHOR_LIST_KEYWORDS) and (
        _contains_any(normalized_message, LIST_INTENT_KEYWORDS) or normalized_message in AUTHOR_LIST_KEYWORDS
    )
    context = {
        "question": message,
        "search_terms": search_terms,
        "store_overview": _get_store_overview(),
        "matched_books": [],
        "matched_categories": [],
        "matched_authors": [],
        "top_sellers": [],
        "store_stats": None,
        "user_orders": None,
        "policies": {},
        "intent": {
            "personal_order_request": personal_order_request,
        },
    }

    if personal_order_request:
        context["matched_books"] = []
    elif price_limit is not None:
        context["price_limit"] = price_limit
        books = (
            Books.objects.select_related(*BOOK_FIELDS)
            .filter(price__lte=price_limit, stock_quantity__gt=0)
            .order_by("price")[:5]
        )
        context["matched_books"] = [_serialize_book(book, include_description=True) for book in books]
    elif _contains_any(normalized_message, CHEAPEST_KEYWORDS):
        books = Books.objects.select_related(*BOOK_FIELDS).filter(stock_quantity__gt=0).order_by("price")[:5]
        context["matched_books"] = [_serialize_book(book, include_description=True) for book in books]
    elif _contains_any(normalized_message, EXPENSIVE_KEYWORDS):
        books = Books.objects.select_related(*BOOK_FIELDS).filter(stock_quantity__gt=0).order_by("-price")[:5]
        context["matched_books"] = [_serialize_book(book, include_description=True) for book in books]
    elif _contains_any(normalized_message, NEWEST_KEYWORDS):
        books = Books.objects.select_related(*BOOK_FIELDS).order_by("-book_id")[:5]
        context["matched_books"] = [_serialize_book(book, include_description=True) for book in books]
    elif _contains_any(normalized_message, ALL_BOOKS_KEYWORDS):
        books = Books.objects.select_related(*BOOK_FIELDS).filter(stock_quantity__gt=0).order_by("title")[:10]
        context["matched_books"] = [_serialize_book(book, include_description=False) for book in books]
    else:
        matched_books = _search_books_by_terms(search_terms, limit=5)
        context["matched_books"] = [
            _serialize_book(book, include_description=True) for book in matched_books
        ]

    if personal_order_request:
        context["matched_categories"] = []
    elif wants_category_listing:
        categories = Categories.objects.all().order_by("name")[:20]
        context["all_categories"] = [
            _serialize_category(category, Books.objects.filter(category=category).count())
            for category in categories
        ]
    else:
        context["matched_categories"] = _search_categories_by_terms(search_terms)

    if personal_order_request:
        context["matched_authors"] = []
    elif wants_author_listing:
        authors = Authors.objects.all().order_by("full_name")[:20]
        context["all_authors"] = [
            _serialize_author(author, Books.objects.filter(author=author).count())
            for author in authors
        ]
    else:
        context["matched_authors"] = _search_authors_by_terms(search_terms)

    if _contains_any(normalized_message, BESTSELLER_KEYWORDS):
        context["top_sellers"] = _get_bestseller_books()

    if _contains_any(normalized_message, STATS_KEYWORDS):
        context["store_stats"] = _get_store_stats()

    if _contains_any(normalized_message, HELP_KEYWORDS) or _contains_any(normalized_message, ORDER_KEYWORDS):
        context["policies"]["order"] = STORE_POLICIES["order"]
    if _contains_any(normalized_message, SHIPPING_KEYWORDS):
        context["policies"]["shipping"] = STORE_POLICIES["shipping"]
    if _contains_any(normalized_message, RETURN_KEYWORDS):
        context["policies"]["return"] = STORE_POLICIES["return"]
    if _contains_any(normalized_message, DISCOUNT_KEYWORDS):
        context["policies"]["discount"] = STORE_POLICIES["discount"]

    if personal_order_request and user_id:
        context["user_orders"] = _get_user_order_context(user_id)

    if (
        not personal_order_request
        and not context["matched_books"]
        and not context["matched_categories"]
        and not context["matched_authors"]
        and not context["top_sellers"]
    ):
        highlight_books = Books.objects.select_related(*BOOK_FIELDS).filter(stock_quantity__gt=0).order_by("-book_id")[:3]
        context["catalog_highlights"] = [
            _serialize_book(book, include_description=True) for book in highlight_books
        ]

    return context


def _render_book_lines(books: list[dict]) -> str:
    return "\n".join(
        [
            f"- {book['title']} | {book['author']} | {_format_currency(book['price'])} | {_format_stock(book['stock'])}"
            for book in books
        ]
    )


def _build_database_fallback_reply(message: str, context: dict, user_id: int | None = None) -> str:
    normalized_message = _normalize_text(message)
    search_terms = context.get("search_terms") or []
    has_specific_search = bool(search_terms)
    personal_order_request = bool(context.get("intent", {}).get("personal_order_request"))

    if _contains_any(normalized_message, GREETING_KEYWORDS):
        return get_chat_reply(message)

    if _contains_any(normalized_message, THANKS_KEYWORDS):
        return get_chat_reply(message)

    if _contains_any(normalized_message, GOODBYE_KEYWORDS):
        return get_chat_reply(message)

    if context.get("user_orders"):
        user_orders = context["user_orders"]
        lines = [
            f"Bạn có {user_orders['order_count']} đơn hàng, tổng chi tiêu {_format_currency(user_orders['total_spent'])}.",
            "Các đơn gần đây:",
        ]
        for order in user_orders["recent_orders"]:
            item_names = ", ".join(item["title"] for item in order["items"] if item["title"]) or "Không có sản phẩm"
            lines.append(
                f"- Đơn #{order['order_id']} | {order['status']} | {_format_currency(order['total_amount'])} | "
                f"{order['order_date']} | {item_names}"
            )
        return "\n".join(lines)

    if personal_order_request and not user_id:
        return "Để kiểm tra đơn hàng của bạn, hãy đăng nhập trước. Sau khi đăng nhập tôi sẽ tra cứu đúng các đơn bạn đã đặt."

    if personal_order_request and user_id and not context.get("user_orders"):
        return "Tôi chưa tìm thấy đơn hàng nào của bạn trong hệ thống."

    if context.get("matched_books"):
        prefix = "Đây là dữ liệu lấy trực tiếp từ database:"
        if context.get("price_limit") is not None:
            prefix = f"Các sách dưới {_format_currency(context['price_limit'])} trong database:"
        elif _contains_any(normalized_message, CHEAPEST_KEYWORDS):
            prefix = "Các sách giá thấp nhất hiện có trong database:"
        elif _contains_any(normalized_message, EXPENSIVE_KEYWORDS):
            prefix = "Các sách giá cao nhất hiện có trong database:"
        elif _contains_any(normalized_message, NEWEST_KEYWORDS):
            prefix = "Các sách mới nhất trong database:"
        return f"{prefix}\n{_render_book_lines(context['matched_books'])}"

    if context.get("top_sellers"):
        return "Các sách bán chạy nhất theo database:\n" + _render_book_lines(context["top_sellers"])

    if context.get("matched_categories"):
        return "Các thể loại khớp với câu hỏi của bạn:\n" + "\n".join(
            f"- {category['name']} ({category['book_count']} sách)" for category in context["matched_categories"]
        )

    if context.get("all_categories"):
        return "Danh sách thể loại hiện có:\n" + "\n".join(
            f"- {category['name']} ({category['book_count']} sách)" for category in context["all_categories"]
        )

    if context.get("matched_authors"):
        return "Các tác giả khớp với câu hỏi của bạn:\n" + "\n".join(
            f"- {author['name']} ({author['book_count']} sách)" for author in context["matched_authors"]
        )

    if context.get("all_authors"):
        return "Danh sách tác giả hiện có:\n" + "\n".join(
            f"- {author['name']} ({author['book_count']} sách)" for author in context["all_authors"]
        )

    if context.get("store_stats"):
        stats = context["store_stats"]
        return (
            f"Thống kê hiện tại từ database:\n"
            f"- Sách: {stats['books']}\n"
            f"- Còn hàng: {stats['in_stock']}\n"
            f"- Hết hàng: {stats['out_of_stock']}\n"
            f"- Đơn hàng: {stats['orders']}\n"
            f"- Doanh thu: {_format_currency(stats['revenue'])}"
        )

    if "shipping" in context["policies"]:
        shipping = context["policies"]["shipping"]
        return (
            "Thông tin giao hàng:\n"
            f"- Phí ship: {shipping['fee']}\n"
            f"- Miễn phí ship từ: {_format_currency(shipping['free_shipping_threshold'])}\n"
            f"- Thời gian dự kiến: {shipping['estimated_time']}"
        )

    if "return" in context["policies"]:
        policy = context["policies"]["return"]
        return (
            "Chính sách đổi trả:\n"
            f"- Thời hạn: {policy['period']}\n"
            f"- Điều kiện: {policy['condition']}\n"
            f"- Hỗ trợ: {policy['support']}"
        )

    if "discount" in context["policies"]:
        return "Ưu đãi hiện có:\n" + "\n".join(f"- {item}" for item in context["policies"]["discount"])

    if "order" in context["policies"]:
        return "Cách đặt hàng:\n" + "\n".join(f"- {step}" for step in context["policies"]["order"])

    if has_specific_search:
        return (
            "Tôi chưa tìm thấy dữ liệu phù hợp trong database"
            f" cho: {', '.join(search_terms[:3])}."
        )

    return get_chat_reply(message)


def build_chat_prompt(message: str, chat_history: list | None, database_context: dict) -> str:
    history_text = _build_history_transcript(chat_history)
    database_text = json.dumps(database_context, ensure_ascii=False, indent=2)

    return f"""Bạn là trợ lý AI của BookStore.

NHIỆM VỤ:
- Trả lời bằng tiếng Việt tự nhiên, rõ ràng, ngắn gọn.
- Ưu tiên tuyệt đối dữ liệu trong mục DATABASE_RESULT cho các câu hỏi về sách, giá, tồn kho, tác giả, thể loại, đơn hàng, thống kê.
- Không bịa dữ liệu. Nếu database không có thông tin phù hợp, nói rõ là chưa tìm thấy trong hệ thống.
- Nếu có danh sách sách, hãy nêu tên sách, tác giả, giá và tình trạng tồn kho.
- Nếu câu hỏi là chung chung ngoài dữ liệu cửa hàng, có thể trả lời ngắn gọn nhưng phải tách bạch với dữ liệu database.

CHAT_HISTORY:
{history_text}

DATABASE_RESULT:
{database_text}

CUSTOMER_QUESTION:
{message}
""".strip()


def get_gemini_reply(message: str, chat_history: list = None, user_id: int | None = None) -> str:
    """
    Gọi Gemini API với dữ liệu truy vấn trực tiếp từ database để trả lời user.

    Args:
        message: Tin nhắn của user
        chat_history: Lịch sử chat gần nhất
        user_id: ID người dùng hiện tại nếu đã đăng nhập

    Returns:
        Câu trả lời cho user
    """
    database_context = build_runtime_context(message, chat_history, user_id)

    try:
        if not model:
            return _build_database_fallback_reply(message, database_context, user_id)

        check_gemini_api_key()
        prompt = build_chat_prompt(message, chat_history, database_context)
        response = model.generate_content(prompt)
        reply = getattr(response, "text", "").strip()
        if reply:
            return reply
    except Exception as error:
        print(f"Gemini Error: {error}")

    return _build_database_fallback_reply(message, database_context, user_id)
