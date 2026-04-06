import datetime
from functools import wraps

import jwt
from django.conf import settings
from rest_framework.response import Response
from .models import Customers

JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24  # 24 giờ


def generate_jwt_token(customer: Customers) -> str:
    payload = {
        'customer_id': customer.customer_id,
        'email': customer.email,
        'role': customer.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def jwt_required(admin_required: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return Response({'error': 'Missing authorization token'}, status=401)

            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return Response({'error': 'Token đã hết hạn'}, status=401)
            except jwt.InvalidTokenError:
                return Response({'error': 'Token không hợp lệ'}, status=401)

            try:
                customer = Customers.objects.get(customer_id=payload.get('customer_id'))
            except Customers.DoesNotExist:
                return Response({'error': 'Token không hợp lệ'}, status=401)

            request.customer = customer
            if admin_required and customer.role != 1:
                return Response({'error': 'Không có quyền truy cập'}, status=403)

            return func(request, *args, **kwargs)
        return wrapper
    return decorator
