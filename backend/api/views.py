from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import Books, Customers, Orders, OrderItems, Authors, Categories, Publishers
from .serializers import BookSerializer
import hashlib
import time
import threading
from .chat_service import get_chat_reply   # ← thêm dòng import này ở đầu views.py
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@api_view(['GET'])
def get_books(request):
    books = Books.objects.select_related('author', 'category', 'publisher').all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_book(request, book_id):
    try:
        book = Books.objects.select_related('author', 'category', 'publisher').get(book_id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def register(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    name = request.data.get('name', '').strip()

    if not email or not password or not name:
        return Response({'error': 'Vui lòng điền đầy đủ thông tin'}, status=status.HTTP_400_BAD_REQUEST)

    if Customers.objects.filter(email=email).exists():
        return Response({'error': 'Email này đã được sử dụng'}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customers.objects.create(
        full_name=name,
        email=email,
        password=hash_password(password),
        role=0,
        created_at=timezone.now().date()
    )

    return Response({
        'id': customer.customer_id,
        'email': customer.email,
        'name': customer.full_name,
        'role': 'admin' if customer.role == 1 else 'user'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'error': 'Vui lòng điền đầy đủ thông tin'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customers.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_400_BAD_REQUEST)

    if customer.password != hash_password(password):
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'id': customer.customer_id,
        'email': customer.email,
        'name': customer.full_name,
        'role': 'admin' if customer.role == 1 else 'user'
    })


@api_view(['POST'])
def create_order(request):
    user_id = request.data.get('user_id')
    items = request.data.get('items', [])
    total_price = request.data.get('total_price', 0)
    address = request.data.get('address', '')
    phone = request.data.get('phone', '')

    if not user_id or not items:
        return Response({'error': 'Thiếu thông tin đặt hàng'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customers.objects.get(customer_id=user_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Người dùng không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    order = Orders.objects.create(
        customer=customer,
        order_date=timezone.now().date(),
        status='pending',
        total_amount=total_price,
        address=address,
        phone=phone
    )

    for item in items:
        book_id = item.get('book_id') or item.get('id')
        try:
            book = Books.objects.get(book_id=book_id)
            OrderItems.objects.create(
                order=order,
                book=book,
                quantity=item.get('quantity', 1),
                unit_price=item.get('price', 0)
            )
        except ObjectDoesNotExist:
            continue

    return Response({
        'success': True,
        'orderId': order.order_id
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_user_orders(request, user_id):
    try:
        orders = Orders.objects.filter(customer_id=user_id).order_by('-order_date')
        result = []
        for order in orders:
            items = OrderItems.objects.filter(order=order).select_related('book')
            result.append({
                'id': order.order_id,
                'status': order.status,
                'total_price': float(order.total_amount),
                'address': order.address,
                'phone': order.phone,
                'created_at': order.order_date,
                'items': [{
                    'title': item.book.title,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price)
                } for item in items]
            })
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_authors(request):
    authors = Authors.objects.all().values('author_id', 'full_name', 'nationality', 'bio')
    return Response(list(authors))


@api_view(['GET'])
def get_categories(request):
    categories = Categories.objects.all().values('category_id', 'name')
    return Response(list(categories))


@api_view(['GET'])
def get_publishers(request):
    publishers = Publishers.objects.all().values('publisher_id', 'name')
    return Response(list(publishers))


@api_view(['POST'])
def create_book(request):
    try:
        title = request.data.get('title', '').strip()
        author_id = request.data.get('author_id')
        category_id = request.data.get('category_id')
        publisher_id = request.data.get('publisher_id')
        price = request.data.get('price', 0)
        stock_quantity = request.data.get('stock_quantity', 0)
        description = request.data.get('description', '')
        image_url = request.data.get('image_url', '')
        isbn = request.data.get('isbn', '').strip()

        if not all([title, author_id, category_id, publisher_id, isbn]):
            return Response({'error': 'Vui lòng điền đầy đủ thông tin'}, status=status.HTTP_400_BAD_REQUEST)

        if Books.objects.filter(isbn=isbn).exists():
            return Response({'error': 'ISBN đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

        book = Books.objects.create(
            title=title,
            author=Authors.objects.get(author_id=author_id),
            category=Categories.objects.get(category_id=category_id),
            publisher=Publishers.objects.get(publisher_id=publisher_id),
            price=price,
            stock_quantity=stock_quantity,
            description=description,
            image_url=image_url,
            isbn=isbn
        )

        return Response({'success': True, 'book_id': book.book_id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_book(request, book_id):
    try:
        book = Books.objects.get(book_id=book_id)
        if 'title' in request.data:
            book.title = request.data['title']
        if 'author_id' in request.data:
            book.author = Authors.objects.get(author_id=request.data['author_id'])
        if 'category_id' in request.data:
            book.category = Categories.objects.get(category_id=request.data['category_id'])
        if 'publisher_id' in request.data:
            book.publisher = Publishers.objects.get(publisher_id=request.data['publisher_id'])
        if 'price' in request.data:
            book.price = request.data['price']
        if 'stock_quantity' in request.data:
            book.stock_quantity = request.data['stock_quantity']
        if 'description' in request.data:
            book.description = request.data['description']
        if 'image_url' in request.data:
            book.image_url = request.data['image_url']
        book.save()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_book(request, book_id):
    try:
        book = Books.objects.get(book_id=book_id)
        book.delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_admin_stats(request):
    books_count = Books.objects.count()
    orders_count = Orders.objects.count()
    users_count = Customers.objects.count()

    # Tính tất cả đơn hàng (không chỉ delivered)
    revenue = Orders.objects.exclude(status='cancelled').aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    # Đơn hàng gần đây nhất
    recent_orders = Orders.objects.select_related('customer').order_by('-order_date')[:5]
    recent = [{
        'id': o.order_id,
        'customer_name': o.customer.full_name,
        'total': float(o.total_amount),
        'status': o.status,
        'date': str(o.order_date),
    } for o in recent_orders]

    # Sách sắp hết hàng (stock < 10)
    low_stock = Books.objects.filter(stock_quantity__lt=10).count()
    # Sách còn hàng tốt (stock >= 10)
    in_stock = Books.objects.filter(stock_quantity__gte=10).count()

    return Response({
        'revenue': float(revenue),
        'orders': orders_count,
        'users': users_count,
        'books': books_count,
        'recent_orders': recent,
        'low_stock': low_stock,
        'in_stock': in_stock,
    })

@api_view(['GET'])
def get_admin_orders(request):
    orders = Orders.objects.select_related('customer').order_by('-order_date')
    result = []
    for order in orders:
        result.append({
            'id': order.order_id,
            'user_name': order.customer.full_name,
            'phone': order.phone or order.customer.phone,
            'total_price': float(order.total_amount),
            'status': order.status,
            'address': order.address,
            'created_at': order.order_date,
        })
    return Response(result)


@api_view(['PATCH'])
def update_order_status(request, order_id):
    try:
        order = Orders.objects.get(order_id=order_id)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_admin_users(request):
    users = Customers.objects.all()
    result = [{
        'id': u.customer_id,
        'name': u.full_name,
        'email': u.email,
        'role': 'admin' if u.role == 1 else 'user'
    } for u in users]
    return Response(result)


# ===== AUTHORS =====
@api_view(['POST'])
def create_author(request):
    full_name = request.data.get('full_name', '').strip()
    bio = request.data.get('bio', '')
    nationality = request.data.get('nationality', '')

    if not full_name:
        return Response({'error': 'Tên tác giả không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    author = Authors.objects.create(full_name=full_name, bio=bio, nationality=nationality)
    return Response({'success': True, 'author_id': author.author_id, 'full_name': author.full_name}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_author(request, author_id):
    try:
        author = Authors.objects.get(author_id=author_id)
        if 'full_name' in request.data:
            author.full_name = request.data['full_name']
        if 'bio' in request.data:
            author.bio = request.data['bio']
        if 'nationality' in request.data:
            author.nationality = request.data['nationality']
        author.save()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy tác giả'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_author(request, author_id):
    try:
        author = Authors.objects.get(author_id=author_id)
        author.delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy tác giả'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Không thể xóa tác giả đang có sách'}, status=status.HTTP_400_BAD_REQUEST)


# ===== CATEGORIES =====
@api_view(['POST'])
def create_category(request):
    name = request.data.get('name', '').strip()
    if not name:
        return Response({'error': 'Tên danh mục không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    category = Categories.objects.create(name=name)
    return Response({'success': True, 'category_id': category.category_id, 'name': category.name}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_category(request, category_id):
    try:
        category = Categories.objects.get(category_id=category_id)
        if 'name' in request.data:
            category.name = request.data['name']
        category.save()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy danh mục'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        category = Categories.objects.get(category_id=category_id)
        category.delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy danh mục'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Không thể xóa danh mục đang có sách'}, status=status.HTTP_400_BAD_REQUEST)
    

_request_times = []
_lock = threading.Lock()
RATE_LIMIT = 12        # max requests
RATE_WINDOW = 60       # trong 60 giây
 
def _check_rate_limit() -> bool:
    """Trả về True nếu còn quota, False nếu đã hết."""
    now = time.time()
    with _lock:
        # Xóa các request cũ hơn 60s
        while _request_times and now - _request_times[0] > RATE_WINDOW:
            _request_times.pop(0)
        if len(_request_times) >= RATE_LIMIT:
            return False
        _request_times.append(now)
        return True
 
# ===== Cache sách (5 phút) =====
_books_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 300  # 5 phút
 
def _get_books_context():
    now = time.time()
    if _books_cache["data"] and now - _books_cache["timestamp"] < CACHE_TTL:
        return _books_cache["data"]
 
    books = Books.objects.select_related('author', 'category').all()
    book_list = '\n'.join([
        f'- Tên: "{b.title}" | Tác giả: {b.author.full_name} | '
        f'Giá: {b.price:,.0f}đ | Còn: {b.stock_quantity} cuốn'
        for b in books
    ])
    result = f"Danh sách sách:\n{book_list}" if book_list else "Chưa có sách nào."
    _books_cache["data"] = result
    _books_cache["timestamp"] = now
    return result
@api_view(['POST'])
def chat(request):
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Tin nhắn không được để trống'}, status=400)
    reply = get_chat_reply(message)
    return Response({'text': reply})
# (giữ nguyên tất cả các hàm khác, chỉ xóa hàm chat() cũ)
@api_view(['POST'])
def chat(request):
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Tin nhắn không được để trống'}, status=400)
    
    reply = get_chat_reply(message)
    return Response({'text': reply})
    message = request.data.get('message', '').strip().lower()

    if not message:
        return Response({'error': 'Tin nhắn không được để trống'}, status=400)

    books = Books.objects.select_related('author', 'category').all()

    # Tìm kiếm theo từ khóa
    matched = books.filter(
        models.Q(title__icontains=message) |
        models.Q(author__full_name__icontains=message) |
        models.Q(category__name__icontains=message) |
        models.Q(description__icontains=message)
    )[:5]

    if matched.exists():
        lines = []
        for b in matched:
            stock_text = f"{b.stock_quantity} cuốn" if b.stock_quantity > 0 else "Hết hàng"
            lines.append(
                f"📖 {b.title}\n"
                f"   Tác giả: {b.author.full_name}\n"
                f"   Thể loại: {b.category.name}\n"
                f"   Giá: {b.price:,.0f}đ\n"
                f"   Tình trạng: {stock_text}"
            )
        return Response({'text': f"Tìm thấy {matched.count()} sách:\n\n" + "\n\n".join(lines)})

    if any(kw in message for kw in ['tất cả', 'danh sách', 'có sách gì', 'có những sách']):
        all_books = books[:10]
        lines = [f"📖 {b.title} - {b.author.full_name} - {b.price:,.0f}đ" for b in all_books]
        total = books.count()
        text = f"Cửa hàng có {total} đầu sách:\n\n" + "\n".join(lines)
        if total > 10:
            text += f"\n\n...và {total - 10} cuốn khác."
        return Response({'text': text})

    if any(kw in message for kw in ['rẻ nhất', 'rẻ', 'giá thấp']):
        cheap = books.filter(stock_quantity__gt=0).order_by('price')[:5]
        lines = [f"📖 {b.title} - {b.price:,.0f}đ" for b in cheap]
        return Response({'text': "Sách giá rẻ nhất:\n\n" + "\n".join(lines)})

    if any(kw in message for kw in ['mới nhất', 'mới', 'vừa ra']):
        new_books = books.order_by('-book_id')[:5]
        lines = [f"📖 {b.title} - {b.author.full_name} - {b.price:,.0f}đ" for b in new_books]
        return Response({'text': "Sách mới nhất:\n\n" + "\n".join(lines)})

    if any(kw in message for kw in ['thể loại', 'loại sách', 'chủ đề']):
        cats = Categories.objects.all()
        lines = [f"• {c.name} ({books.filter(category=c).count()} cuốn)" for c in cats]
        return Response({'text': "Thể loại sách:\n\n" + "\n".join(lines)})

    if any(kw in message for kw in ['tác giả', 'author']):
        authors = Authors.objects.all()[:10]
        lines = [f"• {a.full_name} ({books.filter(author=a).count()} cuốn)" for a in authors]
        return Response({'text': "Tác giả:\n\n" + "\n".join(lines)})

    if any(kw in message for kw in ['xin chào', 'hello', 'hi', 'chào', 'hey']):
        total = books.count()
        return Response({'text': f"Xin chào! 👋 Cửa hàng có {total} đầu sách.\n\nBạn có thể hỏi:\n• Tìm sách theo tên, tác giả, thể loại\n• Sách giá rẻ nhất\n• Sách mới nhất\n• Danh sách thể loại"})

    return Response({'text': (
        "Tôi chưa hiểu câu hỏi 😅\n\n"
        "Bạn thử hỏi:\n"
        "• Tên sách (vd: 'Doraemon')\n"
        "• Tác giả (vd: 'Tô Hoài')\n"
        "• Thể loại (vd: 'thiếu nhi')\n"
        "• 'Sách rẻ nhất' hoặc 'Sách mới nhất'"
    )})