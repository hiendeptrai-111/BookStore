import jwt
import uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


def create_access_token(customer) -> str:
    payload = {
        'jti': uuid.uuid4().hex,
        'customer_id': customer.customer_id,
        'role': 'admin' if customer.role == 1 else 'user',
        'exp': datetime.now(tz=timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def _decode_token(request):
    """Trả về payload dict, raise ValueError nếu token lỗi hoặc thiếu."""
    from .models import BlacklistedToken
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        raise ValueError('Chưa đăng nhập. Vui lòng đăng nhập để tiếp tục.')
    token = auth.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError('Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.')
    except jwt.InvalidTokenError:
        raise ValueError('Token không hợp lệ.')

    jti = payload.get('jti')
    if not jti:
        raise ValueError('Token không hợp lệ, vui lòng đăng nhập lại.')
    if BlacklistedToken.objects.filter(jti=jti).exists():
        raise ValueError('Phiên đăng nhập đã kết thúc, vui lòng đăng nhập lại.')

    return payload


def get_token_payload(request):
    """Trả về (customer_id, role) hoặc raise ValueError."""
    payload = _decode_token(request)
    return payload['customer_id'], payload['role']


def require_auth(request):
    """Dùng trong view: trả về customer_id hoặc Response 401."""
    try:
        customer_id, role = get_token_payload(request)
        return customer_id, role, None
    except ValueError as e:
        return None, None, Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


def require_admin(request):
    """Dùng trong view: trả về customer_id hoặc Response 401/403."""
    try:
        customer_id, role = get_token_payload(request)
        if role != 'admin':
            return None, Response({'error': 'Bạn không có quyền thực hiện thao tác này.'}, status=status.HTTP_403_FORBIDDEN)
        return customer_id, None
    except ValueError as e:
        return None, Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
