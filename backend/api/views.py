from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .models import Books, Customers, Orders, OrderItems, Authors, Categories, Publishers, DiscountCode, Review
from .serializers import BookSerializer
from .auth_utils import create_access_token, require_admin, require_auth
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
    token = create_access_token(customer)

    return Response({
        'id': customer.customer_id,
        'email': customer.email,
        'name': customer.full_name,
        'role': 'admin' if customer.role == 1 else 'user',
        'token': token,
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

    token = create_access_token(customer)
    return Response({
        'id': customer.customer_id,
        'email': customer.email,
        'name': customer.full_name,
        'role': 'admin' if customer.role == 1 else 'user',
        'token': token,
    })


@api_view(['POST'])
def validate_coupon(request):
    code = request.data.get('code', '').strip().upper()
    subtotal = float(request.data.get('subtotal', 0))

    if not code:
        return Response({'valid': False, 'message': 'Vui lòng nhập mã giảm giá'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        coupon = DiscountCode.objects.get(code=code)
    except ObjectDoesNotExist:
        return Response({'valid': False, 'message': 'Mã giảm giá không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    if not coupon.is_active:
        return Response({'valid': False, 'message': 'Mã giảm giá đã bị vô hiệu hóa'}, status=status.HTTP_400_BAD_REQUEST)

    if coupon.expires_at and coupon.expires_at < timezone.now():
        return Response({'valid': False, 'message': 'Mã giảm giá đã hết hạn'}, status=status.HTTP_400_BAD_REQUEST)

    if coupon.max_uses > 0 and coupon.used_count >= coupon.max_uses:
        return Response({'valid': False, 'message': 'Mã giảm giá đã hết lượt sử dụng'}, status=status.HTTP_400_BAD_REQUEST)

    if subtotal < float(coupon.min_order_value):
        return Response({
            'valid': False,
            'message': f'Đơn hàng tối thiểu {coupon.min_order_value:,.0f}đ để dùng mã này'
        }, status=status.HTTP_400_BAD_REQUEST)

    if coupon.discount_type == 'percent':
        discount_amount = subtotal * float(coupon.discount_value) / 100
    else:
        discount_amount = min(float(coupon.discount_value), subtotal)

    return Response({
        'valid': True,
        'discount_amount': round(discount_amount),
        'discount_type': coupon.discount_type,
        'discount_value': float(coupon.discount_value),
        'message': f'Áp dụng mã thành công! Giảm {coupon.discount_value:.0f}{"%" if coupon.discount_type == "percent" else "đ"}'
    })


@api_view(['POST'])
def create_order(request):
    customer_id, _, err = require_auth(request)
    if err:
        return err

    items = request.data.get('items', [])
    total_price = request.data.get('total_price', 0)
    address = request.data.get('address', '')
    phone = request.data.get('phone', '')
    coupon_code = request.data.get('coupon_code', '').strip().upper()

    if not items:
        return Response({'error': 'Thiếu thông tin đặt hàng'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customers.objects.get(customer_id=customer_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Người dùng không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    if coupon_code:
        try:
            coupon = DiscountCode.objects.get(code=coupon_code, is_active=True)
            if coupon.max_uses == 0 or coupon.used_count < coupon.max_uses:
                coupon.used_count += 1
                coupon.save(update_fields=['used_count'])
        except ObjectDoesNotExist:
            pass

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
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
    try:
        book = Books.objects.get(book_id=book_id)
        book.delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_admin_stats(request):
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
    try:
        order = Orders.objects.get(order_id=order_id)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_admin_users(request):
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
    full_name = request.data.get('full_name', '').strip()
    bio = request.data.get('bio', '')
    nationality = request.data.get('nationality', '')

    if not full_name:
        return Response({'error': 'Tên tác giả không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    author = Authors.objects.create(full_name=full_name, bio=bio, nationality=nationality)
    return Response({'success': True, 'author_id': author.author_id, 'full_name': author.full_name}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_author(request, author_id):
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
    name = request.data.get('name', '').strip()
    if not name:
        return Response({'error': 'Tên danh mục không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    category = Categories.objects.create(name=name)
    return Response({'success': True, 'category_id': category.category_id, 'name': category.name}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_category(request, category_id):
    _, err = require_admin(request)
    if err: return err
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
    _, err = require_admin(request)
    if err: return err
    try:
        category = Categories.objects.get(category_id=category_id)
        category.delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy danh mục'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Không thể xóa danh mục đang có sách'}, status=status.HTTP_400_BAD_REQUEST)
    

# ===== DISCOUNT CODES =====
@api_view(['GET'])
def get_admin_coupons(request):
    _, err = require_admin(request)
    if err: return err
    coupons = DiscountCode.objects.all().order_by('-created_at')
    result = [{
        'id': c.id,
        'code': c.code,
        'discount_type': c.discount_type,
        'discount_value': float(c.discount_value),
        'min_order_value': float(c.min_order_value),
        'max_uses': c.max_uses,
        'used_count': c.used_count,
        'is_active': c.is_active,
        'expires_at': c.expires_at.isoformat() if c.expires_at else None,
        'created_at': c.created_at.isoformat(),
    } for c in coupons]
    return Response(result)


@api_view(['POST'])
def create_coupon(request):
    _, err = require_admin(request)
    if err: return err
    code = request.data.get('code', '').strip().upper()
    discount_type = request.data.get('discount_type', '')
    discount_value = request.data.get('discount_value')
    min_order_value = request.data.get('min_order_value', 0)
    max_uses = request.data.get('max_uses', 0)
    expires_at = request.data.get('expires_at')

    if not code or not discount_type or discount_value is None:
        return Response({'error': 'Vui lòng điền đầy đủ thông tin'}, status=status.HTTP_400_BAD_REQUEST)

    if discount_type not in ('percent', 'fixed'):
        return Response({'error': 'Loại giảm giá không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

    if discount_type == 'percent' and float(discount_value) > 100:
        return Response({'error': 'Phần trăm giảm giá không thể vượt quá 100%'}, status=status.HTTP_400_BAD_REQUEST)

    if DiscountCode.objects.filter(code=code).exists():
        return Response({'error': 'Mã giảm giá đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    coupon = DiscountCode.objects.create(
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_value=min_order_value,
        max_uses=max_uses,
        expires_at=expires_at if expires_at else None,
    )
    return Response({'success': True, 'id': coupon.id}, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
def update_coupon(request, coupon_id):
    _, err = require_admin(request)
    if err: return err
    try:
        coupon = DiscountCode.objects.get(id=coupon_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy mã giảm giá'}, status=status.HTTP_404_NOT_FOUND)

    if 'is_active' in request.data:
        coupon.is_active = request.data['is_active']
    if 'discount_value' in request.data:
        coupon.discount_value = request.data['discount_value']
    if 'min_order_value' in request.data:
        coupon.min_order_value = request.data['min_order_value']
    if 'max_uses' in request.data:
        coupon.max_uses = request.data['max_uses']
    if 'expires_at' in request.data:
        coupon.expires_at = request.data['expires_at'] or None
    coupon.save()
    return Response({'success': True})


@api_view(['DELETE'])
def delete_coupon(request, coupon_id):
    _, err = require_admin(request)
    if err: return err
    try:
        coupon = DiscountCode.objects.get(id=coupon_id)
        coupon.delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy mã giảm giá'}, status=status.HTTP_404_NOT_FOUND)


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
@api_view(['GET'])
def get_reviews(request, book_id):
    try:
        book = Books.objects.get(pk=book_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)

    reviews = Review.objects.filter(book=book).select_related('customer')
    data = []
    for r in reviews:
        data.append({
            'id': r.id,
            'customer_name': r.customer.full_name,
            'customer_id': r.customer.customer_id,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat(),
            'admin_reply': r.admin_reply,
            'admin_reply_at': r.admin_reply_at.isoformat() if r.admin_reply_at else None,
        })

    avg = book.reviews.aggregate(avg=models.Avg('rating'))['avg']
    return Response({'reviews': data, 'avg_rating': round(avg, 1) if avg else None, 'count': len(data)})


@api_view(['POST'])
def create_review(request, book_id):
    customer_id, _, err = require_auth(request)
    if err:
        return err

    rating = request.data.get('rating')
    comment = request.data.get('comment', '').strip()
    if not rating or not comment:
        return Response({'error': 'Vui lòng nhập đánh giá và nội dung'}, status=status.HTTP_400_BAD_REQUEST)
    if not (1 <= int(rating) <= 5):
        return Response({'error': 'Điểm đánh giá phải từ 1 đến 5'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Books.objects.get(pk=book_id)
        customer = Customers.objects.get(pk=customer_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách hoặc người dùng'}, status=status.HTTP_404_NOT_FOUND)

    has_ordered = OrderItems.objects.filter(
        order__customer=customer,
        book=book,
        order__status__in=['delivered', 'shipping', 'processing', 'pending'],
    ).exists()
    if not has_ordered:
        return Response({'error': 'Bạn cần mua sách này trước khi đánh giá'}, status=status.HTTP_403_FORBIDDEN)

    review, created = Review.objects.get_or_create(
        book=book,
        customer=customer,
        defaults={'rating': int(rating), 'comment': comment},
    )
    if not created:
        review.rating = int(rating)
        review.comment = comment
        review.save()

    return Response({'success': True, 'id': review.id}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_review(request, review_id):
    customer_id, role, err = require_auth(request)
    if err:
        return err
    try:
        review = Review.objects.get(pk=review_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy đánh giá'}, status=status.HTTP_404_NOT_FOUND)

    if role != 'admin' and review.customer.customer_id != customer_id:
        return Response({'error': 'Bạn không có quyền xóa đánh giá này'}, status=status.HTTP_403_FORBIDDEN)

    review.delete()
    return Response({'success': True})


@api_view(['PATCH'])
def admin_reply_review(request, review_id):
    _, err = require_admin(request)
    if err:
        return err
    try:
        review = Review.objects.get(pk=review_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy đánh giá'}, status=status.HTTP_404_NOT_FOUND)

    reply = request.data.get('reply', '').strip()
    if not reply:
        return Response({'error': 'Nội dung phản hồi không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    review.admin_reply = reply
    review.admin_reply_at = timezone.now()
    review.save()
    return Response({'success': True})


@api_view(['GET'])
def get_admin_reviews(request):
    _, err = require_admin(request)
    if err:
        return err

    reviews = Review.objects.select_related('customer', 'book').all()
    data = [{
        'id': r.id,
        'book_id': r.book.book_id,
        'book_title': r.book.title,
        'customer_name': r.customer.full_name,
        'customer_id': r.customer.customer_id,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.isoformat(),
        'admin_reply': r.admin_reply,
        'admin_reply_at': r.admin_reply_at.isoformat() if r.admin_reply_at else None,
    } for r in reviews]
    return Response(data)


@api_view(['POST'])
def chat(request):
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Tin nhắn không được để trống'}, status=400)
    reply = get_chat_reply(message)
    return Response(reply)