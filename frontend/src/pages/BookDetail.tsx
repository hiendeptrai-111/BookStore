import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShoppingCart, ArrowLeft, ShieldCheck, Truck, RefreshCcw } from 'lucide-react';
import { Book, formatCurrency } from '../types';
import { useApp } from '../AppContext';
import { motion } from 'motion/react';
import { api } from '../services/api';

export const BookDetail: React.FC = () => {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const { addToCart } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    if (id) {
      api.books.getOne(id)
        .then(data => {
          setBook(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!book) return <div className="min-h-screen flex items-center justify-center">Book not found</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <button 
        onClick={() => navigate(-1)}
        className="flex items-center text-sm font-medium text-gray-500 hover:text-indigo-600 mb-8 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Quay lại
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="aspect-[3/4] bg-gray-100 rounded-3xl overflow-hidden shadow-2xl"
        >
          <img 
            src={book.image_url} 
            alt={book.title} 
            className="w-full h-full object-cover"
            referrerPolicy="no-referrer"
          />
        </motion.div>

        <div className="space-y-8">
          <div className="space-y-4">
            <span className="inline-block px-3 py-1 bg-indigo-50 text-indigo-600 text-xs font-bold rounded-full uppercase tracking-wider">
              {book.category}
            </span>
            <h1 className="text-4xl font-extrabold text-gray-900 leading-tight">{book.title}</h1>
            <p className="text-xl text-gray-600">Tác giả: <span className="font-bold text-gray-900">{book.author}</span></p>
            <div className="text-3xl font-extrabold text-indigo-600">{formatCurrency(book.price)}</div>
          </div>

          <div className="prose prose-indigo text-gray-600 max-w-none">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Mô tả nội dung</h3>
            <p>{book.description}</p>
          </div>

          <div className="pt-6 space-y-4">
            <button 
              onClick={() => addToCart(book)}
              className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 flex items-center justify-center"
            >
              <ShoppingCart className="w-5 h-5 mr-2" /> Thêm vào giỏ hàng
            </button>
            <p className="text-center text-sm text-gray-500">Còn lại: {book.stock} cuốn trong kho</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8 border-t border-gray-100">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-50 rounded-lg">
                <Truck className="w-5 h-5 text-green-600" />
              </div>
              <span className="text-xs font-medium text-gray-600">Giao nhanh 2h</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <ShieldCheck className="w-5 h-5 text-blue-600" />
              </div>
              <span className="text-xs font-medium text-gray-600">Bảo hành 12th</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-50 rounded-lg">
                <RefreshCcw className="w-5 h-5 text-orange-600" />
              </div>
              <span className="text-xs font-medium text-gray-600">Đổi trả 7 ngày</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
