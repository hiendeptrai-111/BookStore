from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from .models import Books, Customers, Orders, OrderItems, Authors, Categories, Publishers
from .serializers import BookSerializer
import hashlib


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def customer_payload(customer: Customers) -> dict:
    """Trả về dict chuẩn cho thông tin khách hàng."""
    return {
        'id': customer.customer_id,
        'email': customer.email,
        'name': customer.full_name,
        'role': 'admin' if customer.role == 1 else 'user',
    }


def require_fields(data: dict, *fields):
    """
    Trả về (missing_field, error_response) nếu thiếu trường,
    ngược lại trả về (None, None).
    """
    missing = [f for f in fields if not data.get(f, '')]
    if missing:
        return missing, Response(
            {'error': 'Vui lòng điền đầy đủ thông tin'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None, None


# ──────────────────────────────────────────
# Books
# ──────────────────────────────────────────

BOOK_RELATED = ('author', 'category', 'publisher')


@api_view(['GET'])
def get_books(request):
    books = Books.objects.select_related(*BOOK_RELATED).all()
    return Response(BookSerializer(books, many=True).data)


@api_view(['GET'])
def get_book(request, book_id):
    try:
        book = Books.objects.select_related(*BOOK_RELATED).get(book_id=book_id)
        return Response(BookSerializer(book).data)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_book(request):
    d = request.data
    required = ['title', 'author_id', 'category_id', 'publisher_id', 'isbn']
    _, err = require_fields(d, *required)
    if err:
        return err

    isbn = d['isbn'].strip()
    if Books.objects.filter(isbn=isbn).exists():
        return Response({'error': 'ISBN đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Books.objects.create(
            title=d['title'].strip(),
            author=Authors.objects.get(author_id=d['author_id']),
            category=Categories.objects.get(category_id=d['category_id']),
            publisher=Publishers.objects.get(publisher_id=d['publisher_id']),
            price=d.get('price', 0),
            stock_quantity=d.get('stock_quantity', 0),
            description=d.get('description', ''),
            image_url=d.get('image_url', ''),
            isbn=isbn,
        )
        return Response({'success': True, 'book_id': book.book_id}, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_book(request, book_id):
    try:
        book = Books.objects.get(book_id=book_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)

    d = request.data
    fk_map = {
        'author_id':    ('author',     Authors,     'author_id'),
        'category_id':  ('category',   Categories,  'category_id'),
        'publisher_id': ('publisher',  Publishers,  'publisher_id'),
    }
    direct_fields = ['title', 'price', 'stock_quantity', 'description', 'image_url']

    try:
        for attr in direct_fields:
            if attr in d:
                setattr(book, attr, d[attr])

        for key, (attr, Model, pk_field) in fk_map.items():
            if key in d:
                setattr(book, attr, Model.objects.get(**{pk_field: d[key]}))

        book.save()
        return Response({'success': True})
    except ObjectDoesNotExist as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_book(request, book_id):
    deleted, _ = Books.objects.filter(book_id=book_id).delete()
    if not deleted:
        return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'success': True})


# ──────────────────────────────────────────
# Auth
# ──────────────────────────────────────────

@api_view(['POST'])
def register(request):
    d = request.data
    _, err = require_fields(d, 'email', 'password', 'name')
    if err:
        return err

    email = d['email'].strip()
    
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Email không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
    
    if Customers.objects.filter(email=email).exists():
        return Response({'error': 'Email này đã được sử dụng'}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customers.objects.create(
        full_name=d['name'].strip(),
        email=email,
        password=hash_password(d['password']),
        role=0,
        created_at=timezone.now().date(),
    )
    return Response(customer_payload(customer), status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    d = request.data
    _, err = require_fields(d, 'email', 'password')
    if err:
        return err

    try:
        customer = Customers.objects.get(email=d['email'].strip())
    except ObjectDoesNotExist:
        customer = None  # fall through để tránh timing attack nhẹ

    if not customer or customer.password != hash_password(d['password']):
        return Response(
            {'error': 'Email hoặc mật khẩu không đúng'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(customer_payload(customer))


# ──────────────────────────────────────────
# Orders
# ──────────────────────────────────────────

@api_view(['POST'])
def create_order(request):
    d = request.data
    user_id = d.get('user_id')
    items = d.get('items', [])

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
        total_amount=d.get('total_price', 0),
        address=d.get('address', ''),
        phone=d.get('phone', ''),
    )

    order_items = []
    book_ids = [item.get('book_id') or item.get('id') for item in items]
    books_map = {b.book_id: b for b in Books.objects.filter(book_id__in=book_ids)}

    for item in items:
        bid = item.get('book_id') or item.get('id')
        book = books_map.get(bid)
        if book:
            order_items.append(OrderItems(
                order=order,
                book=book,
                quantity=item.get('quantity', 1),
                unit_price=item.get('price', 0),
            ))
    if order_items:
        OrderItems.objects.bulk_create(order_items)

    return Response({'success': True, 'orderId': order.order_id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_user_orders(request, user_id):
    orders = Orders.objects.filter(customer_id=user_id).prefetch_related(
        models.Prefetch('orderitems_set', queryset=OrderItems.objects.select_related('book'))
    ).order_by('-order_date')

    result = [
        {
            'id': order.order_id,
            'status': order.status,
            'total_price': float(order.total_amount),
            'address': order.address,
            'phone': order.phone,
            'created_at': order.order_date,
            'items': [
                {
                    'title': item.book.title,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                }
                for item in order.orderitems_set.all()
            ],
        }
        for order in orders
    ]
    return Response(result)


@api_view(['GET'])
def get_admin_orders(request):
    orders = Orders.objects.select_related('customer').order_by('-order_date')
    result = [
        {
            'id': o.order_id,
            'user_name': o.customer.full_name,
            'phone': o.phone or o.customer.phone,
            'total_price': float(o.total_amount),
            'status': o.status,
            'address': o.address,
            'created_at': o.order_date,
        }
        for o in orders
    ]
    return Response(result)


@api_view(['PATCH'])
def update_order_status(request, order_id):
    updated = Orders.objects.filter(order_id=order_id).update(
        status=request.data.get('status', '')
    )
    if not updated:
        return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'success': True})


# ──────────────────────────────────────────
# Lookups (Authors / Categories / Publishers)
# ──────────────────────────────────────────

@api_view(['GET'])
def get_authors(request):
    return Response(list(Authors.objects.values('author_id', 'full_name', 'nationality', 'bio')))


@api_view(['GET'])
def get_categories(request):
    return Response(list(Categories.objects.values('category_id', 'name')))


@api_view(['GET'])
def get_publishers(request):
    return Response(list(Publishers.objects.values('publisher_id', 'name')))


# ──────────────────────────────────────────
# Authors CRUD
# ──────────────────────────────────────────

@api_view(['POST'])
def create_author(request):
    full_name = request.data.get('full_name', '').strip()
    if not full_name:
        return Response({'error': 'Tên tác giả không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    author = Authors.objects.create(
        full_name=full_name,
        bio=request.data.get('bio', ''),
        nationality=request.data.get('nationality', ''),
    )
    return Response(
        {'success': True, 'author_id': author.author_id, 'full_name': author.full_name},
        status=status.HTTP_201_CREATED,
    )


@api_view(['PUT'])
def update_author(request, author_id):
    try:
        author = Authors.objects.get(author_id=author_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy tác giả'}, status=status.HTTP_404_NOT_FOUND)

    for field in ('full_name', 'bio', 'nationality'):
        if field in request.data:
            setattr(author, field, request.data[field])
    author.save()
    return Response({'success': True})


@api_view(['DELETE'])
def delete_author(request, author_id):
    try:
        Authors.objects.get(author_id=author_id).delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy tác giả'}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Không thể xóa tác giả đang có sách'}, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
# Categories CRUD
# ──────────────────────────────────────────

@api_view(['POST'])
def create_category(request):
    name = request.data.get('name', '').strip()
    if not name:
        return Response({'error': 'Tên danh mục không được để trống'}, status=status.HTTP_400_BAD_REQUEST)

    category = Categories.objects.create(name=name)
    return Response(
        {'success': True, 'category_id': category.category_id, 'name': category.name},
        status=status.HTTP_201_CREATED,
    )


@api_view(['PUT'])
def update_category(request, category_id):
    try:
        category = Categories.objects.get(category_id=category_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy danh mục'}, status=status.HTTP_404_NOT_FOUND)

    if 'name' in request.data:
        category.name = request.data['name']
    category.save()
    return Response({'success': True})


@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        Categories.objects.get(category_id=category_id).delete()
        return Response({'success': True})
    except ObjectDoesNotExist:
        return Response({'error': 'Không tìm thấy danh mục'}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Không thể xóa danh mục đang có sách'}, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
# Admin Stats
# ──────────────────────────────────────────

@api_view(['GET'])
def get_admin_stats(request):
    revenue = (
        Orders.objects.exclude(status='cancelled')
        .aggregate(total=models.Sum('total_amount'))['total'] or 0
    )

    recent_orders = Orders.objects.select_related('customer').order_by('-order_date')[:5]

    low_stock_qs = Books.objects.aggregate(
        low=models.Count('book_id', filter=models.Q(stock_quantity__lt=10)),
        ok=models.Count('book_id', filter=models.Q(stock_quantity__gte=10)),
    )

    return Response({
        'revenue': float(revenue),
        'orders': Orders.objects.count(),
        'users': Customers.objects.count(),
        'books': Books.objects.count(),
        'recent_orders': [
            {
                'id': o.order_id,
                'customer_name': o.customer.full_name,
                'total': float(o.total_amount),
                'status': o.status,
                'date': str(o.order_date),
            }
            for o in recent_orders
        ],
        'low_stock': low_stock_qs['low'],
        'in_stock': low_stock_qs['ok'],
    })


@api_view(['GET'])
def get_admin_users(request):
    users = Customers.objects.only('customer_id', 'full_name', 'email', 'role')
    return Response([
        {
            'id': u.customer_id,
            'name': u.full_name,
            'email': u.email,
            'role': 'admin' if u.role == 1 else 'user',
        }
        for u in users
    ])