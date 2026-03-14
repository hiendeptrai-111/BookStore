from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Books, Customers
from .serializers import BookSerializer
import hashlib

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
    except Books.DoesNotExist:
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
    except Customers.DoesNotExist:
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_400_BAD_REQUEST)

    if customer.password != hash_password(password):
        return Response({'error': 'Email hoặc mật khẩu không đúng'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'id': customer.customer_id,
        'email': customer.email,
        'name': customer.full_name,
        'role': 'admin' if customer.role == 1 else 'user'
    })