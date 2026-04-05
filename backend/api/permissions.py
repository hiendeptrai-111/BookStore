from rest_framework.permissions import BasePermission


class IsCustomerAuthenticated(BasePermission):
    message = "Bạn cần đăng nhập để thực hiện thao tác này."

    def has_permission(self, request, view):
        return bool(getattr(request.user, "customer_id", None))


class IsAdminCustomer(BasePermission):
    message = "Bạn không có quyền truy cập tài nguyên này."

    def has_permission(self, request, view):
        return bool(getattr(request.user, "customer_id", None) and getattr(request.user, "role", 0) == 1)
