import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from './AppContext';
import { Navbar, Footer } from './components/Layout';
import { Home } from './pages/Home';
import { BookList } from './pages/BookList';
import { BookDetail } from './pages/BookDetail';
import { Cart } from './pages/Cart';
import { Checkout } from './pages/Checkout';
import { MyOrders } from './pages/MyOrders';
import { Login, Register } from './pages/Auth';
import { AdminDashboard, AdminBooks, AdminOrders, AdminUsers, AdminAuthors, AdminCategories, AdminCoupons } from './pages/Admin';
import { LayoutDashboard, Book as BookIcon, ShoppingBag, Users, UserSquare, Tag, Ticket } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { Chatbot } from './components/Chatbot';

const AdminLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useApp();
  const location = useLocation();

  if (!user || user.role !== 'admin') return <Navigate to="/login" />;

  const menu = [
    { name: 'Dashboard', path: '/admin', icon: LayoutDashboard },
    { name: 'Sách', path: '/admin/books', icon: BookIcon },
    { name: 'Tác giả', path: '/admin/authors', icon: UserSquare },
    { name: 'Danh mục', path: '/admin/categories', icon: Tag },
    { name: 'Đơn hàng', path: '/admin/orders', icon: ShoppingBag },
    { name: 'Người dùng', path: '/admin/users', icon: Users },
    { name: 'Mã giảm giá', path: '/admin/coupons', icon: Ticket },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col">
        <div className="p-8">
          <Link to="/" className="text-2xl font-black text-indigo-600 tracking-tighter">ADMIN CP</Link>
        </div>
        <nav className="flex-1 px-4 space-y-2">
          {menu.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all ${
                location.pathname === item.path
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200'
                  : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>
        <div className="p-8 border-t border-gray-100">
          <Link to="/" className="text-sm font-bold text-gray-400 hover:text-indigo-600">Quay lại cửa hàng</Link>
        </div>
      </aside>
      <main className="flex-1 p-12">
        {children}
      </main>
    </div>
  );
};

const UserLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen flex flex-col bg-white">
    <Navbar />
    <main className="flex-1">
      {children}
    </main>
    <Footer />
  </div>
);

export default function App() {
  return (
    <AppProvider>
      <Router>
        <Routes>
          {/* User Routes */}
          <Route path="/" element={<UserLayout><Home /></UserLayout>} />
          <Route path="/books" element={<UserLayout><BookList /></UserLayout>} />
          <Route path="/books/:id" element={<UserLayout><BookDetail /></UserLayout>} />
          <Route path="/cart" element={<UserLayout><Cart /></UserLayout>} />
          <Route path="/checkout" element={<UserLayout><Checkout /></UserLayout>} />
          <Route path="/orders" element={<UserLayout><MyOrders /></UserLayout>} />
          <Route path="/login" element={<UserLayout><Login /></UserLayout>} />
          <Route path="/register" element={<UserLayout><Register /></UserLayout>} />

          {/* Admin Routes */}
          <Route path="/admin" element={<AdminLayout><AdminDashboard /></AdminLayout>} />
          <Route path="/admin/books" element={<AdminLayout><AdminBooks /></AdminLayout>} />
          <Route path="/admin/authors" element={<AdminLayout><AdminAuthors /></AdminLayout>} />
          <Route path="/admin/categories" element={<AdminLayout><AdminCategories /></AdminLayout>} />
          <Route path="/admin/orders" element={<AdminLayout><AdminOrders /></AdminLayout>} />
          <Route path="/admin/users" element={<AdminLayout><AdminUsers /></AdminLayout>} />
          <Route path="/admin/coupons" element={<AdminLayout><AdminCoupons /></AdminLayout>} />
        </Routes>
        <Chatbot />
      </Router>
    </AppProvider>
  );
}