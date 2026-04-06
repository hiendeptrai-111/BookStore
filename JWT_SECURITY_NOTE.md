# Note cac file lien quan den bao mat JWT

## Backend

### [backend/api/auth_utils.py](D:\BookStore\backend\api\auth_utils.py)
- File trung tam cho JWT.
- `generate_jwt_token()` tao token voi cac claim: `customer_id`, `email`, `role`, `exp`, `iat`.
- `jwt_required()` doc header `Authorization: Bearer <token>`, giai ma token, kiem tra het han, kiem tra hop le, nap `request.customer`.
- Co phan quyen admin qua `admin_required=True`.

### [backend/api/views.py](D:\BookStore\backend\api\views.py)
- Noi phat hanh JWT khi:
- `register()` tao user moi va tra ve `token`.
- `login_view()` dang nhap thanh cong va tra ve `token`.
- Noi ap dung bao ve JWT qua `@jwt_required()`:
- `create_order`
- `get_user_orders`
- Cac API admin voi `@jwt_required(admin_required=True)`:
- `create_book`
- `update_book`
- `delete_book`
- `get_admin_stats`
- `get_admin_orders`
- `update_order_status`
- `get_admin_users`
- `create_author`
- `update_author`
- `delete_author`
- `create_category`
- `update_category`
- `delete_category`
- File nay cung tu hash mat khau bang `sha256`, lien quan den auth nhung khong phai JWT truc tiep.

### [backend/api/urls.py](D:\BookStore\backend\api\urls.py)
- Khai bao cac route lien quan den auth va cac route duoc bao ve bang JWT.
- Hai route auth chinh:
- `/auth/register/`
- `/auth/login/`
- Cac route `/orders/*` va `/admin/*` la nhung diem can doi chieu voi `views.py` de xem co dang duoc bao ve dung khong.

### [backend/backend/settings.py](D:\BookStore\backend\backend\settings.py)
- Chua `SECRET_KEY`, hien dang duoc dung lam `JWT_SECRET`.
- Day la file cuc ky quan trong voi bao mat JWT vi neu lo secret thi co the gia mao token.
- Co `CORS_ALLOWED_ORIGINS`, anh huong den frontend khi gui `Authorization` header.
- Hien tai thay `DEBUG = True` va `SECRET_KEY` hard-code trong source.

### [backend/requirements.txt](D:\BookStore\backend\requirements.txt)
- Chua dependency `PyJWT`, thu vien dung de encode/decode token.

## Frontend

### [frontend/src/AppContext.tsx](D:\BookStore\frontend\src\AppContext.tsx)
- Noi luu `token` trong state va dong bo vao `localStorage`.
- `logout()` xoa token.
- Day la diem quan trong vi token dang duoc luu o `localStorage`.

### [frontend/src/services/api.ts](D:\BookStore\frontend\src\services\api.ts)
- Ham `request()` doc token tu `localStorage`.
- Tu dong gan header `Authorization: Bearer ${token}` cho cac request.
- Day la file client-side chinh lien quan den viec su dung JWT.

### [frontend/src/pages/Auth.tsx](D:\BookStore\frontend\src\pages\Auth.tsx)
- Goi `api.auth.login()` va `api.auth.register()`.
- Sau khi nhan du lieu user tu backend, `setUser(data)` duoc goi.
- Can doi chieu them voi kieu `User`/luong du lieu de chac chan token duoc dua vao context dung cach.

### [frontend/src/pages/Admin.tsx](D:\BookStore\frontend\src\pages\Admin.tsx)
- Nhieu request admin tu gan header `Authorization: Bearer ...`.
- Co su dung ca `token` tu context va `localStorage.getItem('token')`.
- Day la file frontend co mat do su dung JWT/Bearer token nhieu nhat.

## Chu y bao mat nhanh

- `SECRET_KEY` dang nam truc tiep trong [backend/backend/settings.py](D:\BookStore\backend\backend\settings.py), nen dua sang bien moi truong.
- Token dang duoc luu trong `localStorage` tai [frontend/src/AppContext.tsx](D:\BookStore\frontend\src\AppContext.tsx), co rui ro neu xay ra XSS.
- JWT dang dung chung `SECRET_KEY` cua Django trong [backend/api/auth_utils.py](D:\BookStore\backend\api\auth_utils.py), nen tach rieng `JWT_SECRET`.
- Khong thay co refresh token, revoke token, rotation, hoac blacklist.
- Khong thay middleware/auth class tap trung; viec bao ve dang dua vao decorator tu viet.
