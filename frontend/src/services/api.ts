import { AuthResponse, Book, Order, User } from "../types";
import {
  clearAuthSession,
  getStoredTokens,
  type StoredTokens,
  setStoredTokens,
} from "./authStorage";

const API_BASE_URL = import.meta.env.VITE_API_URL || "";
const IS_MOCK = false;

const mockRequest = async <T>(action: () => T): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(action()), 300);
  });
};

function normalizeBook(book: any): Book {
  return {
    ...book,
    id: book.book_id,
    author_id: book.author,
    author: book.author_name || book.author,
    category_id: book.category,
    category: book.category_name || book.category,
    publisher_id: book.publisher,
    publisher: book.publisher_name || book.publisher,
    stock: book.stock_quantity,
    image_url: book.image_url || `https://picsum.photos/seed/book${book.book_id}/400/600`,
    description: book.description || "",
  };
}

function normalizeAuthResponse(data: any): AuthResponse {
  return {
    user: {
      id: data.user.id,
      email: data.user.email,
      name: data.user.name,
      role: data.user.role,
    },
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
  };
}

async function refreshAccessToken(tokens: StoredTokens): Promise<StoredTokens | null> {
  const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: tokens.refreshToken }),
  });

  if (!response.ok) {
    return null;
  }

  const data = await response.json();
  const nextTokens: StoredTokens = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token || tokens.refreshToken,
  };
  setStoredTokens(nextTokens);
  return nextTokens;
}

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  allowRetry = true,
): Promise<Response> {
  if (IS_MOCK) {
    throw new Error("Mock mode does not support apiFetch");
  }

  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const tokens = getStoredTokens();
  if (tokens?.accessToken) {
    headers.set("Authorization", `Bearer ${tokens.accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status !== 401 || !allowRetry || !tokens?.refreshToken || path === "/auth/refresh/") {
    if (response.status === 401 && tokens?.refreshToken && path !== "/auth/login/" && path !== "/auth/register/") {
      clearAuthSession();
    }
    return response;
  }

  const refreshedTokens = await refreshAccessToken(tokens);
  if (!refreshedTokens) {
    clearAuthSession();
    return response;
  }

  const retryHeaders = new Headers(options.headers || {});
  if (options.body && !retryHeaders.has("Content-Type")) {
    retryHeaders.set("Content-Type", "application/json");
  }
  retryHeaders.set("Authorization", `Bearer ${refreshedTokens.accessToken}`);

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: retryHeaders,
  });
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (IS_MOCK) {
    if (path === "/auth/login/") {
      const { email } = JSON.parse(options.body as string);
      return mockRequest(() => {
        const users = JSON.parse(localStorage.getItem("mock_users") || "[]");
        const user = users.find((item: any) => item.email === email);
        if (!user) throw new Error("Email hoặc mật khẩu không đúng");
        return user;
      }) as Promise<T>;
    }

    if (path === "/auth/register/") {
      const { email, name } = JSON.parse(options.body as string);
      return mockRequest(() => {
        const users = JSON.parse(localStorage.getItem("mock_users") || "[]");
        if (users.find((item: any) => item.email === email)) {
          throw new Error("Email này đã được sử dụng");
        }
        const newUser = { id: Date.now(), email, name, role: "user" };
        localStorage.setItem("mock_users", JSON.stringify([...users, newUser]));
        return newUser;
      }) as Promise<T>;
    }

    return mockRequest(() => [] as any);
  }

  const response = await apiFetch(path, options);
  const raw = await response.text();
  const data = raw ? JSON.parse(raw) : null;

  if (!response.ok) {
    throw new Error(data?.error || data?.detail || "Something went wrong");
  }

  return data;
}

export const api = {
  books: {
    getAll: () => request<any[]>("/books/").then((data) => data.map(normalizeBook)),
    getOne: (id: string | number) => request<any>(`/books/${id}/`).then(normalizeBook),
    create: (book: Partial<Book>) =>
      request<{ success: boolean }>("/admin/books/", {
        method: "POST",
        body: JSON.stringify(book),
      }),
    update: (id: string | number, book: Partial<Book>) =>
      request<{ success: boolean }>(`/admin/books/${id}/`, {
        method: "PUT",
        body: JSON.stringify(book),
      }),
    delete: (id: string | number) =>
      request<{ success: boolean }>(`/admin/books/${id}/delete/`, {
        method: "DELETE",
      }),
  },

  auth: {
    login: (credentials: any) =>
      request<any>("/auth/login/", {
        method: "POST",
        body: JSON.stringify(credentials),
      }).then(normalizeAuthResponse),

    register: (userData: any) =>
      request<any>("/auth/register/", {
        method: "POST",
        body: JSON.stringify(userData),
      }).then(normalizeAuthResponse),
  },

  orders: {
    create: (orderData: any) =>
      request<{ success: boolean; orderId: number }>("/orders/", {
        method: "POST",
        body: JSON.stringify(orderData),
      }),

    getUserOrders: (userId: number) => request<Order[]>(`/orders/user/${userId}/`),

    getAll: () => request<Order[]>("/admin/orders/"),

    updateStatus: (id: number, status: string) =>
      request<{ success: boolean }>(`/admin/orders/${id}/status/`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
  },

  admin: {
    getStats: () => request<any>("/admin/stats/"),
    getUsers: () => request<User[]>("/admin/users/"),
    getAuthors: () => request<any[]>("/admin/authors/"),
    getCategories: () => request<any[]>("/admin/categories/"),
    getPublishers: () => request<any[]>("/admin/publishers/"),
    createAuthor: (payload: any) =>
      request<any>("/admin/authors/create/", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    updateAuthor: (id: number, payload: any) =>
      request<any>(`/admin/authors/${id}/`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    deleteAuthor: (id: number) =>
      request<any>(`/admin/authors/${id}/delete/`, {
        method: "DELETE",
      }),
    createCategory: (payload: any) =>
      request<any>("/admin/categories/create/", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    updateCategory: (id: number, payload: any) =>
      request<any>(`/admin/categories/${id}/`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    deleteCategory: (id: number) =>
      request<any>(`/admin/categories/${id}/delete/`, {
        method: "DELETE",
      }),
  },
};
