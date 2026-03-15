from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class AuthServiceTest(TestCase):
    """Test Auth: Đăng ký và đăng nhập"""

    def setUp(self):
        self.client = APIClient()

    @patch('api.views.Customers')
    def test_register_success(self, MockCustomers):
        """Test đăng ký thành công"""
        MockCustomers.objects.filter.return_value.exists.return_value = False
        mock_customer = MagicMock()
        mock_customer.customer_id = 1
        mock_customer.email = 'test@example.com'
        mock_customer.full_name = 'Test User'
        mock_customer.role = 0
        MockCustomers.objects.create.return_value = mock_customer

        res = self.client.post('/api/auth/register/', {
            'email': 'test@example.com',
            'password': '123456',
            'name': 'Test User'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['email'], 'test@example.com')
        self.assertEqual(res.data['role'], 'user')

    @patch('api.views.Customers')
    def test_register_duplicate_email(self, MockCustomers):
        """Test đăng ký email đã tồn tại"""
        MockCustomers.objects.filter.return_value.exists.return_value = True

        res = self.client.post('/api/auth/register/', {
            'email': 'exist@example.com',
            'password': '123456',
            'name': 'New User'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

    def test_register_missing_fields(self):
        """Test đăng ký thiếu thông tin"""
        res = self.client.post('/api/auth/register/', {
            'email': 'test@example.com',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Customers')
    def test_login_success(self, MockCustomers):
        """Test đăng nhập thành công"""
        mock_customer = MagicMock()
        mock_customer.customer_id = 1
        mock_customer.email = 'login@example.com'
        mock_customer.full_name = 'Login User'
        mock_customer.password = hash_password('password123')
        mock_customer.role = 0
        MockCustomers.objects.get.return_value = mock_customer

        res = self.client.post('/api/auth/login/', {
            'email': 'login@example.com',
            'password': 'password123'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], 'login@example.com')
        self.assertEqual(res.data['role'], 'user')

    @patch('api.views.Customers')
    def test_login_wrong_password(self, MockCustomers):
        """Test đăng nhập sai mật khẩu"""
        mock_customer = MagicMock()
        mock_customer.password = hash_password('correct_password')
        MockCustomers.objects.get.return_value = mock_customer

        res = self.client.post('/api/auth/login/', {
            'email': 'user@example.com',
            'password': 'wrong_password'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

    @patch('api.views.Customers')
    def test_login_not_found(self, MockCustomers):
        """Test đăng nhập email không tồn tại"""
        from api.models import Customers as RealCustomers
        MockCustomers.objects.get.side_effect = RealCustomers.DoesNotExist

        res = self.client.post('/api/auth/login/', {
            'email': 'notfound@example.com',
            'password': '123456'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test đăng nhập thiếu thông tin"""
        res = self.client.post('/api/auth/login/', {
            'email': '',
            'password': ''
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class BookServiceTest(TestCase):
    """Test CRUD Books"""

    def setUp(self):
        self.client = APIClient()

    @patch('api.views.BookSerializer')
    @patch('api.views.Books')
    def test_get_all_books(self, MockBooks, MockSerializer):
        """Test lấy danh sách sách"""
        MockBooks.objects.select_related.return_value.all.return_value = []
        MockSerializer.return_value.data = []

        res = self.client.get('/api/books/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('api.views.BookSerializer')
    @patch('api.views.Books')
    def test_get_single_book(self, MockBooks, MockSerializer):
        """Test lấy chi tiết 1 cuốn sách"""
        mock_book = MagicMock()
        MockBooks.objects.select_related.return_value.get.return_value = mock_book
        MockSerializer.return_value.data = {'book_id': 1, 'title': 'Test Book'}

        res = self.client.get('/api/books/1/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('api.views.Books')
    def test_get_book_not_found(self, MockBooks):
        """Test lấy sách không tồn tại"""
        from api.models import Books as RealBooks
        MockBooks.objects.select_related.return_value.get.side_effect = RealBooks.DoesNotExist

        res = self.client.get('/api/books/99999/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @patch('api.views.Books')
    @patch('api.views.Authors')
    @patch('api.views.Categories')
    @patch('api.views.Publishers')
    def test_create_book_success(self, MockPublishers, MockCategories, MockAuthors, MockBooks):
        """Test thêm sách thành công"""
        MockBooks.objects.filter.return_value.exists.return_value = False
        mock_book = MagicMock()
        mock_book.book_id = 1
        MockBooks.objects.create.return_value = mock_book
        MockAuthors.objects.get.return_value = MagicMock()
        MockCategories.objects.get.return_value = MagicMock()
        MockPublishers.objects.get.return_value = MagicMock()

        res = self.client.post('/api/admin/books/', {
            'isbn': '978-000-000-002',
            'title': 'New Book',
            'author_id': 1,
            'category_id': 1,
            'publisher_id': 1,
            'price': 75000,
            'stock_quantity': 20,
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])

    def test_create_book_missing_fields(self):
        """Test thêm sách thiếu thông tin bắt buộc"""
        res = self.client.post('/api/admin/books/', {
            'title': 'Missing Fields Book',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Books')
    def test_create_book_duplicate_isbn(self, MockBooks):
        """Test thêm sách trùng ISBN"""
        MockBooks.objects.filter.return_value.exists.return_value = True

        res = self.client.post('/api/admin/books/', {
            'isbn': '978-000-000-001',
            'title': 'Duplicate',
            'author_id': 1,
            'category_id': 1,
            'publisher_id': 1,
            'price': 50000,
            'stock_quantity': 5
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

    @patch('api.views.Books')
    def test_update_book(self, MockBooks):
        """Test cập nhật sách"""
        mock_book = MagicMock()
        MockBooks.objects.get.return_value = mock_book

        res = self.client.put('/api/admin/books/1/', {
            'title': 'Updated Title',
            'price': 99000
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])

    @patch('api.views.Books')
    def test_delete_book(self, MockBooks):
        """Test xóa sách"""
        mock_book = MagicMock()
        MockBooks.objects.get.return_value = mock_book

        res = self.client.delete('/api/admin/books/1/delete/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_book.delete.assert_called_once()


class AuthorServiceTest(TestCase):
    """Test CRUD Authors"""

    def setUp(self):
        self.client = APIClient()

    @patch('api.views.Authors')
    def test_get_authors(self, MockAuthors):
        """Test lấy danh sách tác giả"""
        MockAuthors.objects.all.return_value.values.return_value = []

        res = self.client.get('/api/admin/authors/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('api.views.Authors')
    def test_create_author_success(self, MockAuthors):
        """Test thêm tác giả thành công"""
        mock_author = MagicMock()
        mock_author.author_id = 1
        mock_author.full_name = 'New Author'
        MockAuthors.objects.create.return_value = mock_author

        res = self.client.post('/api/admin/authors/create/', {
            'full_name': 'New Author',
            'nationality': 'Vietnamese'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['full_name'], 'New Author')

    def test_create_author_missing_name(self):
        """Test thêm tác giả không có tên"""
        res = self.client.post('/api/admin/authors/create/', {
            'nationality': 'American'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Authors')
    def test_update_author(self, MockAuthors):
        """Test cập nhật tác giả"""
        mock_author = MagicMock()
        MockAuthors.objects.get.return_value = mock_author

        res = self.client.put('/api/admin/authors/1/', {
            'full_name': 'Updated Author',
            'nationality': 'French'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])

    @patch('api.views.Authors')
    def test_delete_author(self, MockAuthors):
        """Test xóa tác giả"""
        mock_author = MagicMock()
        MockAuthors.objects.get.return_value = mock_author

        res = self.client.delete('/api/admin/authors/1/delete/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_author.delete.assert_called_once()


class CategoryServiceTest(TestCase):
    """Test CRUD Categories"""

    def setUp(self):
        self.client = APIClient()

    @patch('api.views.Categories')
    def test_get_categories(self, MockCategories):
        """Test lấy danh sách danh mục"""
        MockCategories.objects.all.return_value.values.return_value = []

        res = self.client.get('/api/admin/categories/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('api.views.Categories')
    def test_create_category_success(self, MockCategories):
        """Test thêm danh mục thành công"""
        mock_cat = MagicMock()
        mock_cat.category_id = 1
        mock_cat.name = 'New Category'
        MockCategories.objects.create.return_value = mock_cat

        res = self.client.post('/api/admin/categories/create/', {
            'name': 'New Category'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_category_empty_name(self):
        """Test thêm danh mục tên trống"""
        res = self.client.post('/api/admin/categories/create/', {
            'name': ''
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Categories')
    def test_update_category(self, MockCategories):
        """Test cập nhật danh mục"""
        mock_cat = MagicMock()
        MockCategories.objects.get.return_value = mock_cat

        res = self.client.put('/api/admin/categories/1/', {
            'name': 'Updated Category'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('api.views.Categories')
    def test_delete_category(self, MockCategories):
        """Test xóa danh mục"""
        mock_cat = MagicMock()
        MockCategories.objects.get.return_value = mock_cat

        res = self.client.delete('/api/admin/categories/1/delete/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_cat.delete.assert_called_once()


class OrderServiceTest(TestCase):
    """Test Đặt hàng"""

    def setUp(self):
        self.client = APIClient()

    @patch('api.views.Orders')
    @patch('api.views.OrderItems')
    @patch('api.views.Books')
    @patch('api.views.Customers')
    def test_create_order_success(self, MockCustomers, MockBooks, MockOrderItems, MockOrders):
        """Test đặt hàng thành công"""
        mock_customer = MagicMock()
        MockCustomers.objects.get.return_value = mock_customer
        mock_book = MagicMock()
        MockBooks.objects.get.return_value = mock_book
        mock_order = MagicMock()
        mock_order.order_id = 1
        MockOrders.objects.create.return_value = mock_order

        res = self.client.post('/api/orders/', {
            'user_id': 1,
            'items': [{'id': 1, 'quantity': 2, 'price': 89000}],
            'total_price': 178000,
            'address': '123 Test Street',
            'phone': '0909090909'
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])

    def test_create_order_missing_items(self):
        """Test đặt hàng không có sản phẩm"""
        res = self.client.post('/api/orders/', {
            'user_id': 1,
            'items': [],
            'total_price': 0
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('api.views.Customers')
    def test_create_order_invalid_user(self, MockCustomers):
        """Test đặt hàng với user không tồn tại"""
        from api.models import Customers as RealCustomers
        MockCustomers.objects.get.side_effect = RealCustomers.DoesNotExist

        res = self.client.post('/api/orders/', {
            'user_id': 99999,
            'items': [{'id': 1, 'quantity': 1, 'price': 89000}],
            'total_price': 89000
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)