import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ArrowRight, ShoppingBag } from 'lucide-react';
import { useApp } from '../AppContext';
import { formatCurrency } from '../types';
import { motion } from 'motion/react';

export const Cart: React.FC = () => {
  const { cart, removeFromCart, updateCartQuantity } = useApp();
  const navigate = useNavigate();

  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const shipping = subtotal > 500000 ? 0 : 30000;
  const total = subtotal + shipping;

  if (cart.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="bg-indigo-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
          <ShoppingBag className="w-10 h-10 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Giỏ hàng trống</h2>
        <p className="text-gray-500 mb-8">Bạn chưa thêm cuốn sách nào vào giỏ hàng của mình.</p>
        <Link to="/books" className="bg-indigo-600 text-white px-8 py-3 rounded-full font-bold hover:bg-indigo-700 transition-all">
          Tiếp tục mua sắm
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-10">Giỏ hàng của bạn</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-2 space-y-6">
          {cart.map((item) => (
            <motion.div 
              layout
              key={item.id}
              className="flex items-center space-x-6 bg-white p-6 rounded-2xl border border-gray-100"
            >
              <div className="w-24 h-32 flex-shrink-0 bg-gray-100 rounded-xl overflow-hidden">
                <img src={item.image_url} alt={item.title} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-gray-900 truncate">{item.title}</h3>
                <p className="text-sm text-gray-500">{item.author}</p>
                <p className="text-indigo-600 font-bold mt-2">{formatCurrency(item.price)}</p>
              </div>
              <div className="flex items-center space-x-3 bg-gray-50 p-1 rounded-xl">
                <button 
                  onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                  className="p-1 hover:bg-white rounded-lg transition-colors"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <span className="w-8 text-center font-bold text-gray-900">{item.quantity}</span>
                <button 
                  onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                  className="p-1 hover:bg-white rounded-lg transition-colors"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              <button 
                onClick={() => removeFromCart(item.id)}
                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </motion.div>
          ))}
        </div>

        <div className="space-y-6">
          <div className="bg-gray-50 p-8 rounded-3xl space-y-6">
            <h3 className="text-xl font-bold text-gray-900">Tóm tắt đơn hàng</h3>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between text-gray-600">
                <span>Tạm tính</span>
                <span>{formatCurrency(subtotal)}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Phí vận chuyển</span>
                <span>{shipping === 0 ? 'Miễn phí' : formatCurrency(shipping)}</span>
              </div>
              <div className="pt-4 border-t border-gray-200 flex justify-between text-lg font-bold text-gray-900">
                <span>Tổng cộng</span>
                <span>{formatCurrency(total)}</span>
              </div>
            </div>
            <button 
              onClick={() => navigate('/checkout')}
              className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 flex items-center justify-center"
            >
              Thanh toán ngay <ArrowRight className="ml-2 w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-center text-gray-400">
            Bằng cách nhấn thanh toán, bạn đồng ý với các điều khoản dịch vụ của chúng tôi.
          </p>
        </div>
      </div>
    </div>
  );
};
