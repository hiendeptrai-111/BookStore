import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(amount);
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: "user" | "admin";
}

export interface Book {
  book_id: number;
  id: number;        // alias để không lỗi chỗ khác
  isbn: string;
  title: string;
  author: number;
  author_name: string;
  category: number;
  category_name: string;
  publisher: number;
  publisher_name: string;
  price: number;
  stock_quantity: number;
  stock: number;     // alias
  description?: string;
  image_url?: string;
}

export interface Order {
  id: number;
  user_id: number;
  total_price: number;
  status: "pending" | "confirmed" | "shipped" | "delivered" | "cancelled";
  address: string;
  phone: string;
  created_at: string;
  user_name?: string;
}

export interface CartItem extends Book {
  quantity: number;
}

export interface ChatBookCard {
  id: number;
  title: string;
  author: string;
  price: number;
  image_url: string | null;
  stock: number;
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  books?: ChatBookCard[];
}

export interface DiscountCode {
  id: number;
  code: string;
  discount_type: 'percent' | 'fixed';
  discount_value: number;
  min_order_value: number;
  max_uses: number;
  used_count: number;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
}
