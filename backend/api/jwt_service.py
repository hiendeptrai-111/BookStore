from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


JWT_ALGORITHM = "HS256"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _secret_key() -> str:
    return getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)


def _build_payload(customer, token_type: str, expires_at: datetime) -> dict:
    return {
        "sub": str(customer.customer_id),
        "email": customer.email,
        "role": "admin" if customer.role == 1 else "user",
        "type": token_type,
        "iat": int(_now().timestamp()),
        "exp": int(expires_at.timestamp()),
    }


def generate_access_token(customer) -> str:
    expires_at = _now() + timedelta(minutes=getattr(settings, "JWT_ACCESS_TOKEN_MINUTES", 60))
    payload = _build_payload(customer, "access", expires_at)
    return jwt.encode(payload, _secret_key(), algorithm=JWT_ALGORITHM)


def generate_refresh_token(customer) -> str:
    expires_at = _now() + timedelta(days=getattr(settings, "JWT_REFRESH_TOKEN_DAYS", 7))
    payload = _build_payload(customer, "refresh", expires_at)
    return jwt.encode(payload, _secret_key(), algorithm=JWT_ALGORITHM)


def generate_token_pair(customer) -> dict:
    return {
        "access_token": generate_access_token(customer),
        "refresh_token": generate_refresh_token(customer),
    }


def decode_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationFailed("Token đã hết hạn.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed("Token không hợp lệ.") from exc

    if expected_type and payload.get("type") != expected_type:
        raise AuthenticationFailed("Loại token không hợp lệ.")

    return payload
