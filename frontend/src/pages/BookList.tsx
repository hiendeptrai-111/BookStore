import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Filter, ShoppingCart } from 'lucide-react';
import { Book, formatCurrency } from '../types';
import { useApp } from '../AppContext';
import { motion } from 'motion/react';
import { api } from '../services/api';

export const BookList: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [filteredBooks, setFilteredBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const { addToCart } = useApp();
  const location = useLocation();

  // Đọc ?search= từ URL khi navigate từ Navbar
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('search') || '';
    setSearch(q);
  }, [location.search]);

  useEffect(() => {
    api.books.getAll()
      .then(data => {
        setBooks(data);
        setFilteredBooks(data);
      })
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    let result = books;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(b =>
        (b.title || '').toLowerCase().includes(q) ||
        (typeof b.author === 'string' ? b.author : '').toLowerCase().includes(q)
      );
    }
    if (category !== 'All') {
      result = result.filter(b =>
        (typeof b.category === 'string' ? b.category : '') === category
      );
    }
    setFilteredBooks(result);
  }, [search, category, books]);

  const categories = ['All', ...new Set(
    books.map(b => typeof b.category === 'string' ? b.category : '').filter(Boolean)
  )];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tất cả sách</h1>
          <p className="text-gray-500 mt-1">Tìm thấy {filteredBooks.length} cuốn sách phù hợp</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Tìm theo tên hoặc tác giả..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 w-full sm:w-64"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="pl-10 pr-8 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 appearance-none w-full"
            >
              {categories.map(c => (
                <option key={c} value={c}>{c === 'All' ? 'Tất cả thể loại' : c}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        {filteredBooks.map((book) => (
          <motion.div
            layout
            key={book.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="group bg-white rounded-2xl overflow-hidden border border-gray-100 hover:shadow-xl transition-all"
          >
            <Link to={`/books/${book.id}`}>
              <div className="aspect-[2/3] overflow-hidden bg-gray-100">
                <img
                  src={book.image_url || `https://picsum.photos/seed/book${book.id}/400/600`}
                  alt={book.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  referrerPolicy="no-referrer"
                />
              </div>
            </Link>
            <div className="p-4 space-y-2">
              <p className="text-[10px] font-bold text-indigo-600 uppercase tracking-widest">{book.category}</p>
              <Link to={`/books/${book.id}`}>
                <h3 className="font-bold text-gray-900 line-clamp-1 group-hover:text-indigo-600 transition-colors">
                  {book.title}
                </h3>
              </Link>
              <p className="text-xs text-gray-500">{book.author}</p>
              <div className="flex items-center justify-between pt-2">
                <span className="font-bold text-indigo-600">{formatCurrency(book.price)}</span>
                <button
                  onClick={() => addToCart(book)}
                  className="p-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-600 hover:text-white transition-all"
                >
                  <ShoppingCart className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredBooks.length === 0 && (
        <div className="text-center py-20">
          <p className="text-gray-500 text-lg">Không tìm thấy cuốn sách nào phù hợp với yêu cầu của bạn.</p>
        </div>
      )}
    </div>
  );
};