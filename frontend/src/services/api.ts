import { Book, User, Order } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const IS_MOCK = false;

// --- HELPER FOR MOCK API ---
const mockRequest = async <T>(action: () => T): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(action()), 300);
  });
};

// --- NORMALIZE BOOK: chuyển field từ backend sang frontend ---
function normalizeBook(book: any): Book {
  return {
    ...book,
    id: book.book_id,
    author: book.author_name || book.author,
    category: book.category_name || book.category,
    stock: book.stock_quantity,
    image_url: book.image_url || `https://picsum.photos/seed/book${book.book_id}/400/600`,
    description: book.description || '',
  };
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (IS_MOCK) {
    if (path === '/auth/login/') {
      const { email } = JSON.parse(options.body as string);
      return mockRequest(() => {
        const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
        const user = users.find((u: any) => u.email === email);
        if (!user) throw new Error('Email hoặc mật khẩu không đúng');
        return user;
      }) as Promise<T>;
    }
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
  books: {
    getAll: () => request<any[]>('/books/').then(data => data.map(normalizeBook)),
    getOne: (id: string | number) => request<any>(`/books/${id}/`).then(normalizeBook),
    create: (book: Partial<Book>) => request<{ success: boolean }>('/admin/books/', {
      method: 'POST',
      body: JSON.stringify(book),
    }),
    update: (id: string | number, book: Partial<Book>) => request<{ success: boolean }>(`/admin/books/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(book),
    }),
    delete: (id: string | number) => request<{ success: boolean }>(`/admin/books/${id}/`, {
      method: 'DELETE',
    }),
  },
  auth: {
    login: (credentials: any) => request<User>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
    register: (userData: any) => request<User>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
  },
  orders: {
    create: (orderData: any) => request<{ success: boolean; orderId: number }>('/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),
    getUserOrders: (userId: number) => request<Order[]>(`/orders/user/${userId}/`),
    getAll: () => request<Order[]>('/admin/orders/'),
    updateStatus: (id: number, status: string) => request<{ success: boolean }>(`/admin/orders/${id}/status/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  },
  admin: {
    getStats: () => request<any>('/admin/stats/'),
    getUsers: () => request<User[]>('/admin/users/'),
  },
};