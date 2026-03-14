from django.urls import path
from .views import get_books, get_book, register, login_view

urlpatterns = [
    path('books/', get_books),
    path('books/<int:book_id>/', get_book),
    path('auth/register/', register),
    path('auth/login/', login_view),
]