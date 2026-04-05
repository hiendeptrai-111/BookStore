import hashlib
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def make_authenticated_customer(customer_id=1, role=0):
    return SimpleNamespace(
        customer_id=customer_id,
        role=role,
        is_authenticated=True,
        is_anonymous=False,
    )


class AuthServiceTest(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('api.views.Customers')
    def test_register_success(self, mock_customers):
        mock_customers.objects.filter.return_value.exists.return_value = False
        mock_customer = MagicMock()
        mock_customer.customer_id = 1
        mock_customer.email = 'test@example.com'
        mock_customer.full_name = 'Test User'
        mock_customer.role = 0
        mock_customers.objects.create.return_value = mock_customer

        response = self.client.post(
            '/api/auth/register/',
            {'email': 'test@example.com', 'password': '123456', 'name': 'Test User'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['role'], 'user')
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    @patch('api.views.Customers')
    def test_register_duplicate_email(self, mock_customers):
        mock_customers.objects.filter.return_value.exists.return_value = True

        response = self.client.post(
            '/api/auth/register/',
            {'email': 'exist@example.com', 'password': '123456', 'name': 'New User'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post(
            '/api/auth/register/',
            {'email': 'test@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Customers')
    def test_login_success(self, mock_customers):
        mock_customer = MagicMock()
        mock_customer.customer_id = 1
        mock_customer.email = 'login@example.com'
        mock_customer.full_name = 'Login User'
        mock_customer.password = hash_password('password123')
        mock_customer.role = 0
        mock_customers.objects.get.return_value = mock_customer

        response = self.client.post(
            '/api/auth/login/',
            {'email': 'login@example.com', 'password': 'password123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'login@example.com')
        self.assertEqual(response.data['user']['role'], 'user')
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    @patch('api.views.Customers')
    def test_login_wrong_password(self, mock_customers):
        mock_customer = MagicMock()
        mock_customer.password = hash_password('correct_password')
        mock_customers.objects.get.return_value = mock_customer

        response = self.client.post(
            '/api/auth/login/',
            {'email': 'user@example.com', 'password': 'wrong_password'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('api.views.Customers')
    def test_login_not_found(self, mock_customers):
        from api.models import Customers as real_customers

        mock_customers.objects.get.side_effect = real_customers.DoesNotExist

        response = self.client.post(
            '/api/auth/login/',
            {'email': 'notfound@example.com', 'password': '123456'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': '', 'password': ''},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Customers')
    @patch('api.views.decode_token')
    def test_refresh_token_success(self, mock_decode_token, mock_customers):
        mock_decode_token.return_value = {'sub': '1', 'type': 'refresh'}
        mock_customer = MagicMock()
        mock_customer.customer_id = 1
        mock_customer.email = 'refresh@example.com'
        mock_customer.full_name = 'Refresh User'
        mock_customer.role = 0
        mock_customers.objects.get.return_value = mock_customer

        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh_token': 'valid-refresh-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_refresh_token_missing_token(self):
        response = self.client.post(
            '/api/auth/refresh/',
            {'refresh_token': ''},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_requires_auth(self):
        response = self.client.post(
            '/api/orders/',
            {'items': [{'id': 1, 'quantity': 1, 'price': 89000}], 'total_price': 89000},
            format='json',
        )

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )


class BookServiceTest(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = make_authenticated_customer(role=1)
        self.client.force_authenticate(user=self.admin_user)

    @patch('api.views.BookSerializer')
    @patch('api.views.Books')
    def test_get_all_books(self, mock_books, mock_serializer):
        mock_books.objects.select_related.return_value.all.return_value = []
        mock_serializer.return_value.data = []

        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.BookSerializer')
    @patch('api.views.Books')
    def test_get_single_book(self, mock_books, mock_serializer):
        mock_book = MagicMock()
        mock_books.objects.select_related.return_value.get.return_value = mock_book
        mock_serializer.return_value.data = {'book_id': 1, 'title': 'Test Book'}

        response = self.client.get('/api/books/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.Books')
    def test_get_book_not_found(self, mock_books):
        from api.models import Books as real_books

        mock_books.objects.select_related.return_value.get.side_effect = real_books.DoesNotExist

        response = self.client.get('/api/books/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('api.views.Publishers')
    @patch('api.views.Categories')
    @patch('api.views.Authors')
    @patch('api.views.Books')
    def test_create_book_success(self, mock_books, mock_authors, mock_categories, mock_publishers):
        mock_books.objects.filter.return_value.exists.return_value = False
        mock_book = MagicMock()
        mock_book.book_id = 1
        mock_books.objects.create.return_value = mock_book
        mock_authors.objects.get.return_value = MagicMock()
        mock_categories.objects.get.return_value = MagicMock()
        mock_publishers.objects.get.return_value = MagicMock()

        response = self.client.post(
            '/api/admin/books/',
            {
                'isbn': '978-000-000-002',
                'title': 'New Book',
                'author_id': 1,
                'category_id': 1,
                'publisher_id': 1,
                'price': 75000,
                'stock_quantity': 20,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    def test_create_book_missing_fields(self):
        response = self.client.post(
            '/api/admin/books/',
            {'title': 'Missing Fields Book'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Books')
    def test_create_book_duplicate_isbn(self, mock_books):
        mock_books.objects.filter.return_value.exists.return_value = True

        response = self.client.post(
            '/api/admin/books/',
            {
                'isbn': '978-000-000-001',
                'title': 'Duplicate',
                'author_id': 1,
                'category_id': 1,
                'publisher_id': 1,
                'price': 50000,
                'stock_quantity': 5,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('api.views.Books')
    def test_update_book(self, mock_books):
        mock_book = MagicMock()
        mock_books.objects.get.return_value = mock_book

        response = self.client.put(
            '/api/admin/books/1/',
            {'title': 'Updated Title', 'price': 99000},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    @patch('api.views.Books')
    def test_delete_book(self, mock_books):
        mock_book = MagicMock()
        mock_books.objects.get.return_value = mock_book

        response = self.client.delete('/api/admin/books/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_book.delete.assert_called_once()


class AuthorServiceTest(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=make_authenticated_customer(role=1))

    @patch('api.views.Authors')
    def test_get_authors(self, mock_authors):
        mock_authors.objects.all.return_value.values.return_value = []

        response = self.client.get('/api/admin/authors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.Authors')
    def test_create_author_success(self, mock_authors):
        mock_author = MagicMock()
        mock_author.author_id = 1
        mock_author.full_name = 'New Author'
        mock_authors.objects.create.return_value = mock_author

        response = self.client.post(
            '/api/admin/authors/create/',
            {'full_name': 'New Author', 'nationality': 'Vietnamese'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], 'New Author')

    def test_create_author_missing_name(self):
        response = self.client.post(
            '/api/admin/authors/create/',
            {'nationality': 'American'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Authors')
    def test_update_author(self, mock_authors):
        mock_author = MagicMock()
        mock_authors.objects.get.return_value = mock_author

        response = self.client.put(
            '/api/admin/authors/1/',
            {'full_name': 'Updated Author', 'nationality': 'French'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    @patch('api.views.Authors')
    def test_delete_author(self, mock_authors):
        mock_author = MagicMock()
        mock_authors.objects.get.return_value = mock_author

        response = self.client.delete('/api/admin/authors/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_author.delete.assert_called_once()


class CategoryServiceTest(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=make_authenticated_customer(role=1))

    @patch('api.views.Categories')
    def test_get_categories(self, mock_categories):
        mock_categories.objects.all.return_value.values.return_value = []

        response = self.client.get('/api/admin/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.Categories')
    def test_create_category_success(self, mock_categories):
        mock_category = MagicMock()
        mock_category.category_id = 1
        mock_category.name = 'New Category'
        mock_categories.objects.create.return_value = mock_category

        response = self.client.post(
            '/api/admin/categories/create/',
            {'name': 'New Category'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_empty_name(self):
        response = self.client.post(
            '/api/admin/categories/create/',
            {'name': ''},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Categories')
    def test_update_category(self, mock_categories):
        mock_category = MagicMock()
        mock_categories.objects.get.return_value = mock_category

        response = self.client.put(
            '/api/admin/categories/1/',
            {'name': 'Updated Category'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.views.Categories')
    def test_delete_category(self, mock_categories):
        mock_category = MagicMock()
        mock_categories.objects.get.return_value = mock_category

        response = self.client.delete('/api/admin/categories/1/delete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_category.delete.assert_called_once()


class OrderServiceTest(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = make_authenticated_customer(customer_id=1, role=0)
        self.client.force_authenticate(user=self.customer)

    @patch('api.views.Orders')
    @patch('api.views.OrderItems')
    @patch('api.views.Books')
    def test_create_order_success(self, mock_books, mock_order_items, mock_orders):
        mock_book = MagicMock()
        mock_books.objects.get.return_value = mock_book
        mock_order = MagicMock()
        mock_order.order_id = 1
        mock_orders.objects.create.return_value = mock_order

        response = self.client.post(
            '/api/orders/',
            {
                'items': [{'id': 1, 'quantity': 2, 'price': 89000}],
                'total_price': 178000,
                'address': '123 Test Street',
                'phone': '0909090909',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        mock_order_items.objects.create.assert_called()

    def test_create_order_missing_items(self):
        response = self.client.post(
            '/api/orders/',
            {'items': [], 'total_price': 0},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
