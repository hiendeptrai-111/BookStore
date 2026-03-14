import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, User as UserIcon, LogOut, BookOpen, Search } from 'lucide-react';
import { useApp } from '../AppContext';
import { formatCurrency } from '../types';

export const Navbar: React.FC = () => {
  const { user, cart, logout } = useApp();
  const navigate = useNavigate();

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center space-x-2">
            <BookOpen className="w-8 h-8 text-indigo-600" />
            <span className="text-xl font-bold text-gray-900 tracking-tight">BookStore</span>
          </Link>

          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input 
                type="text" 
                placeholder="Tìm kiếm sách..." 
                className="w-full pl-10 pr-4 py-2 bg-gray-50 border-none rounded-full text-sm focus:ring-2 focus:ring-indigo-500 transition-all"
              />
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <Link to="/books" className="text-sm font-medium text-gray-600 hover:text-indigo-600 transition-colors">
              Cửa hàng
            </Link>
            
            <Link to="/cart" className="relative p-2 text-gray-600 hover:text-indigo-600 transition-colors">
              <ShoppingCart className="w-6 h-6" />
              {cartCount > 0 && (
                <span className="absolute top-0 right-0 bg-indigo-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                  {cartCount}
                </span>
              )}
            </Link>

            {user ? (
              <div className="flex items-center space-x-4">
                <Link to={user.role === 'admin' ? "/admin" : "/orders"} className="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-indigo-600">
                  <UserIcon className="w-5 h-5" />
                  <span className="hidden sm:inline">{user.name}</span>
                </Link>
                <button 
                  onClick={() => { logout(); navigate('/'); }}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link to="/login" className="text-sm font-medium text-gray-700 hover:text-indigo-600">
                  Đăng nhập
                </Link>
                <Link to="/register" className="bg-indigo-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-200">
                  Đăng ký
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export const Footer: React.FC = () => (
  <footer className="bg-gray-50 border-t border-gray-200 py-12">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="col-span-1 md:col-span-2">
          <div className="flex items-center space-x-2 mb-4">
            <BookOpen className="w-6 h-6 text-indigo-600" />
            <span className="text-lg font-bold text-gray-900">BookStore</span>
          </div>
          <p className="text-gray-500 text-sm max-w-xs">
            Nơi hội tụ những tri thức tinh hoa của nhân loại. Chúng tôi mang đến cho bạn những cuốn sách chất lượng nhất.
          </p>
        </div>
        <div>
          <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4">Liên kết</h4>
          <ul className="space-y-2 text-sm text-gray-600">
            <li><Link to="/" className="hover:text-indigo-600">Trang chủ</Link></li>
            <li><Link to="/books" className="hover:text-indigo-600">Tất cả sách</Link></li>
            <li><Link to="/cart" className="hover:text-indigo-600">Giỏ hàng</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4">Hỗ trợ</h4>
          <ul className="space-y-2 text-sm text-gray-600">
            <li><Link to="#" className="hover:text-indigo-600">Chính sách đổi trả</Link></li>
            <li><Link to="#" className="hover:text-indigo-600">Vận chuyển</Link></li>
            <li><Link to="#" className="hover:text-indigo-600">Liên hệ</Link></li>
          </ul>
        </div>
      </div>
      <div className="mt-12 pt-8 border-t border-gray-200 text-center text-sm text-gray-400">
        &copy; {new Date().getFullYear()} BookStore. All rights reserved.
      </div>
    </div>
  </footer>
);
