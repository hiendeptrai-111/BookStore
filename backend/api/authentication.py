from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .jwt_service import decode_token
from .models import Customers


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None

        if auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) != 2:
            raise AuthenticationFailed("Authorization header không hợp lệ.")

        try:
            token = auth[1].decode()
        except UnicodeDecodeError as exc:
            raise AuthenticationFailed("Token không hợp lệ.") from exc

        payload = decode_token(token, expected_type="access")

        try:
            customer = Customers.objects.get(customer_id=int(payload["sub"]))
        except (Customers.DoesNotExist, ValueError, TypeError) as exc:
            raise AuthenticationFailed("Người dùng không tồn tại.") from exc

        return customer, payload

    def authenticate_header(self, request):
        return self.keyword
