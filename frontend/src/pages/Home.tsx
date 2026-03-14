import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { ArrowRight, Star, TrendingUp, ShieldCheck, Truck } from 'lucide-react';
import { Book, formatCurrency } from '../types';
import { useApp } from '../AppContext';
import { api } from '../services/api';

export const Home: React.FC = () => {
  const [featuredBooks, setFeaturedBooks] = useState<Book[]>([]);
  const { addToCart } = useApp();

  useEffect(() => {
    api.books.getAll()
      .then(data => setFeaturedBooks(data.slice(0, 4)))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-indigo-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight">
                Khám phá thế giới <br />
                <span className="text-indigo-600">qua từng trang sách</span>
              </h1>
              <p className="text-lg text-gray-600 max-w-lg">
                Hàng ngàn đầu sách từ văn học, kinh tế đến kỹ năng sống đang chờ đón bạn. 
                Bắt đầu hành trình tri thức ngay hôm nay.
              </p>
              <div className="flex space-x-4">
                <Link to="/books" className="bg-indigo-600 text-white px-8 py-4 rounded-full font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 flex items-center">
                  Mua ngay <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
                <Link to="/books" className="bg-white text-gray-900 px-8 py-4 rounded-full font-bold border border-gray-200 hover:border-indigo-600 transition-all">
                  Xem danh mục
                </Link>
              </div>
            </motion.div>
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <img 
                src="https://picsum.photos/seed/library/800/600" 
                alt="Hero" 
                className="rounded-3xl shadow-2xl rotate-2 hover:rotate-0 transition-transform duration-500"
                referrerPolicy="no-referrer"
              />
              <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-2xl shadow-xl flex items-center space-x-4">
                <div className="bg-green-100 p-3 rounded-full">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Bán chạy nhất</p>
                  <p className="text-lg font-bold text-gray-900">+1,200 cuốn tuần này</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: Truck, title: "Giao hàng nhanh", desc: "Miễn phí vận chuyển cho đơn hàng từ 500k" },
            { icon: ShieldCheck, title: "Sách chính hãng", desc: "Cam kết 100% sách thật từ các nhà xuất bản" },
            { icon: Star, title: "Ưu đãi thành viên", desc: "Tích điểm đổi quà và nhận mã giảm giá mỗi tháng" }
          ].map((f, i) => (
            <div key={i} className="bg-white p-8 rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow">
              <f.icon className="w-10 h-10 text-indigo-600 mb-4" />
              <h3 className="text-lg font-bold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured Books */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-10">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Sách nổi bật</h2>
            <p className="text-gray-500 mt-2">Những cuốn sách được yêu thích nhất hiện nay</p>
          </div>
          <Link to="/books" className="text-indigo-600 font-bold flex items-center hover:underline">
            Xem tất cả <ArrowRight className="ml-1 w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {featuredBooks.map((book) => (
            <motion.div 
              key={book.id}
              whileHover={{ y: -5 }}
              className="group bg-white rounded-2xl overflow-hidden border border-gray-100 hover:shadow-xl transition-all"
            >
              <Link to={`/books/${book.id}`}>
                <div className="aspect-[2/3] overflow-hidden bg-gray-100">
                  <img 
                    src={book.image_url} 
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
                    <Star className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
};
