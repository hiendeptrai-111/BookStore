import { Book, User, Order } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const IS_MOCK = !API_BASE_URL || API_BASE_URL === 'http://localhost:8000/api';

// --- MOCK DATA SEEDING ---
const initialBooks: Book[] = [
  { id: 1, title: 'Đắc Nhân Tâm', author: 'Dale Carnegie', price: 85000, description: 'Cuốn sách hay nhất mọi thời đại về nghệ thuật giao tiếp.', image_url: 'https://picsum.photos/seed/book1/400/600', category: 'Kỹ năng sống', stock: 50 },
  { id: 2, title: 'Nhà Giả Kim', author: 'Paulo Coelho', price: 79000, description: 'Hành trình đi tìm vận mệnh của chàng chăn cừu Santiago.', image_url: 'https://picsum.photos/seed/book2/400/600', category: 'Văn học', stock: 30 },
  { id: 3, title: 'Cha Giàu Cha Nghèo', author: 'Robert Kiyosaki', price: 125000, description: 'Bài học về tài chính cá nhân từ hai người cha.', image_url: 'https://picsum.photos/seed/book3/400/600', category: 'Kinh tế', stock: 20 },
  { id: 4, title: 'Sapiens', author: 'Yuval Noah Harari', price: 195000, description: 'Lược sử loài người từ thời kỳ đồ đá đến hiện đại.', image_url: 'https://picsum.photos/seed/book4/400/600', category: 'Khoa học', stock: 15 },
  { id: 5, title: 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh', author: 'Nguyễn Nhật Ánh', price: 92000, description: 'Câu chuyện cảm động về tuổi thơ ở làng quê Việt Nam.', image_url: 'https://picsum.photos/seed/book5/400/600', category: 'Văn học', stock: 45 },
];

if (IS_MOCK && !localStorage.getItem('mock_books')) {
  localStorage.setItem('mock_books', JSON.stringify(initialBooks));
  localStorage.setItem('mock_orders', JSON.stringify([]));
  localStorage.setItem('mock_users', JSON.stringify([
    { id: 1, name: 'Admin', email: 'admin@example.com', role: 'admin' },
    { id: 2, name: 'Người dùng mẫu', email: 'user@example.com', role: 'user' }
  ]));
}

// --- HELPER FOR MOCK API ---
const mockRequest = async <T>(action: () => T): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(action()), 300);
  });
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (IS_MOCK) {
    // Logic giả lập cho các endpoint
    if (path === '/books') {
      return mockRequest(() => JSON.parse(localStorage.getItem('mock_books') || '[]')) as Promise<T>;
    }
    if (path.startsWith('/books/')) {
      const id = parseInt(path.split('/').pop() || '0');
      return mockRequest(() => {
        const books = JSON.parse(localStorage.getItem('mock_books') || '[]');
        return books.find((b: any) => b.id === id);
      }) as Promise<T>;
    }
    if (path === '/auth/login') {
      const { email } = JSON.parse(options.body as string);
      return mockRequest(() => {
        const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
        const user = users.find((u: any) => u.email === email);
        if (!user) throw new Error('Email hoặc mật khẩu không đúng');
        return user;
      }) as Promise<T>;
    }
    if (path === '/orders' && options.method === 'POST') {
      const orderData = JSON.parse(options.body as string);
      return mockRequest(() => {
        const orders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
        const newOrder = { ...orderData, id: Date.now(), created_at: new Date().toISOString(), status: 'pending' };
        localStorage.setItem('mock_orders', JSON.stringify([...orders, newOrder]));
        return { success: true, orderId: newOrder.id };
      }) as Promise<T>;
    }
    if (path.startsWith('/orders/user/')) {
      const userId = parseInt(path.split('/').pop() || '0');
      return mockRequest(() => {
        const orders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
        return orders.filter((o: any) => o.user_id === userId);
      }) as Promise<T>;
    }
    if (path === '/admin/stats') {
      return mockRequest(() => {
        const books = JSON.parse(localStorage.getItem('mock_books') || '[]');
        const orders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
        const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
        const revenue = orders.reduce((sum: number, o: any) => sum + o.total_price, 0);
        return { revenue, orders: orders.length, users: users.length, books: books.length };
      }) as Promise<T>;
    }
    // Các endpoint khác...
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
  books: {
    getAll: () => request<Book[]>('/books'),
    getOne: (id: string | number) => request<Book>(`/books/${id}`),
    create: (book: Partial<Book>) => request<{ success: boolean }>('/admin/books', {
      method: 'POST',
      body: JSON.stringify(book),
    }),
    update: (id: string | number, book: Partial<Book>) => request<{ success: boolean }>(`/admin/books/${id}`, {
      method: 'PUT',
      body: JSON.stringify(book),
    }),
    delete: (id: string | number) => request<{ success: boolean }>(`/admin/books/${id}`, {
      method: 'DELETE',
    }),
  },
  auth: {
    login: (credentials: any) => request<User>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
    register: (userData: any) => request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
  },
  orders: {
    create: (orderData: any) => request<{ success: boolean; orderId: number }>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),
    getUserOrders: (userId: number) => request<Order[]>(`/orders/user/${userId}`),
    getAll: () => request<Order[]>('/admin/orders'),
    updateStatus: (id: number, status: string) => request<{ success: boolean }>(`/admin/orders/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  },
  admin: {
    getStats: () => request<any>('/admin/stats'),
    getUsers: () => request<User[]>('/admin/users'),
  },
};
