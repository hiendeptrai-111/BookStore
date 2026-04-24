import { Book, User, Order, DiscountCode } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const IS_MOCK = false;

// --- HELPER FOR MOCK API ---
// Giả lập độ trễ mạng 300ms khi dùng mock data (không gọi API thật)
const mockRequest = async <T>(action: () => T): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(action()), 300);
  });
};

// --- NORMALIZE BOOK: chuyển field từ backend sang frontend ---
// Dùng để chuẩn hóa dữ liệu sách từ backend trước khi hiển thị ra UI
function normalizeBook(book: any): Book {
  return {
    ...book,
    id: book.book_id,                                                                        // map book_id → id
    author: book.author_name || book.author,                                                 // tên tác giả
    category: book.category_name || book.category,                                           // tên danh mục
    stock: book.stock_quantity,                                                              // số lượng tồn kho
    image_url: book.image_url || `https://picsum.photos/seed/book${book.book_id}/400/600`,  // ảnh mặc định nếu không có
    description: book.description || '',                                                     // mô tả sách
  };
}

// --- HÀM GỌI API CHUNG ---
// Xử lý cả 2 chế độ: mock (IS_MOCK=true) và real API (IS_MOCK=false)
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (IS_MOCK) {
    // Mock: đăng nhập
    if (path === '/auth/login/') {
      const { email } = JSON.parse(options.body as string);
      return mockRequest(() => {
        const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
        const user = users.find((u: any) => u.email === email);
        if (!user) throw new Error('Email hoặc mật khẩu không đúng');
        return user;
      }) as Promise<T>;
    }
    // Mock: đăng ký
    if (path === '/auth/register/') {
      const { email, name } = JSON.parse(options.body as string);
      return mockRequest(() => {
        const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
        if (users.find((u: any) => u.email === email)) {
          throw new Error('Email này đã được sử dụng');
        }
        const newUser = { id: Date.now(), email, name, role: 'user' };
        localStorage.setItem('mock_users', JSON.stringify([...users, newUser]));
        return newUser;
      }) as Promise<T>;
    }
    return mockRequest(() => ([] as any));
  }

  // Real API Request
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Something went wrong');
  return data;
}

export const api = {
  // --- SÁCH ---
  books: {
    // [HIỂN THỊ DANH SÁCH SÁCH] Lấy toàn bộ sách → dùng cho trang BookList
    getAll: () => request<any[]>('/books/').then(data => data.map(normalizeBook)),

    // [CHI TIẾT SÁCH] Lấy 1 cuốn sách theo id → dùng cho trang BookDetail
    getOne: (id: string | number) => request<any>(`/books/${id}/`).then(normalizeBook),

    // [ADMIN] Thêm sách mới
    create: (book: Partial<Book>) => request<{ success: boolean }>('/admin/books/', {
      method: 'POST',
      body: JSON.stringify(book),
    }),

    // [ADMIN] Cập nhật thông tin sách
    update: (id: string | number, book: Partial<Book>) => request<{ success: boolean }>(`/admin/books/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(book),
    }),

    // [ADMIN] Xóa sách
    delete: (id: string | number) => request<{ success: boolean }>(`/admin/books/${id}/`, {
      method: 'DELETE',
    }),
  },

  // --- XÁC THỰC ---
  auth: {
    // Đăng nhập → trả về thông tin User
    login: (credentials: any) => request<User>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

    // Đăng ký tài khoản mới
    register: (userData: any) => request<User>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
  },

  // --- ĐƠN HÀNG ---
  orders: {
    // Tạo đơn hàng mới
    create: (orderData: any) => request<{ success: boolean; orderId: number }>('/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),

    // Lấy danh sách đơn hàng của 1 user
    getUserOrders: (userId: number) => request<Order[]>(`/orders/user/${userId}/`),

    // [ADMIN] Lấy tất cả đơn hàng
    getAll: () => request<Order[]>('/admin/orders/'),

    // [ADMIN] Cập nhật trạng thái đơn hàng
    updateStatus: (id: number, status: string) => request<{ success: boolean }>(`/admin/orders/${id}/status/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  },

  // --- ADMIN ---
  admin: {
    getStats: () => request<any>('/admin/stats/'),
    getUsers: () => request<User[]>('/admin/users/'),
  },

  // --- MÃ GIẢM GIÁ ---
  coupons: {
    validate: (code: string, subtotal: number) =>
      request<{ valid: boolean; discount_amount: number; discount_type: string; discount_value: number; message: string }>(
        '/coupons/validate/',
        { method: 'POST', body: JSON.stringify({ code, subtotal }) }
      ),

    getAll: () => request<DiscountCode[]>('/admin/coupons/'),

    create: (data: Partial<DiscountCode>) =>
      request<{ success: boolean; id: number }>('/admin/coupons/create/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: number, data: Partial<DiscountCode>) =>
      request<{ success: boolean }>(`/admin/coupons/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),

    delete: (id: number) =>
      request<{ success: boolean }>(`/admin/coupons/${id}/delete/`, {
        method: 'DELETE',
      }),
  },
};