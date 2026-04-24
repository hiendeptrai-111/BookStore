import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShoppingCart, ArrowLeft, ShieldCheck, Truck, RefreshCcw, Star } from 'lucide-react';
import { Book, Review, formatCurrency } from '../types';
import { useApp } from '../AppContext';
import { motion } from 'motion/react';
import { api } from '../services/api';

const StarRating: React.FC<{ value: number; onChange?: (v: number) => void }> = ({ value, onChange }) => (
  <div className="flex gap-1">
    {[1, 2, 3, 4, 5].map(n => (
      <Star
        key={n}
        className={`w-5 h-5 ${n <= value ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'} ${onChange ? 'cursor-pointer' : ''}`}
        onClick={() => onChange?.(n)}
      />
    ))}
  </div>
);

export const BookDetail: React.FC = () => {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const { addToCart, user } = useApp();
  const navigate = useNavigate();

  const [reviews, setReviews] = useState<Review[]>([]);
  const [avgRating, setAvgRating] = useState<number | null>(null);
  const [myRating, setMyRating] = useState(5);
  const [myComment, setMyComment] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [reviewSuccess, setReviewSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadReviews = (bookId: string) => {
    api.reviews.getByBook(bookId).then(res => {
      setReviews(res.reviews);
      setAvgRating(res.avg_rating);
    });
  };

  useEffect(() => {
    if (id) {
      api.books.getOne(id)
        .then(data => { setBook(data); setLoading(false); })
        .catch(err => { console.error(err); setLoading(false); });
      loadReviews(id);
    }
  }, [id]);

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setReviewError('');
    setReviewSuccess('');
    setSubmitting(true);
    try {
      await api.reviews.create(id, { rating: myRating, comment: myComment });
      setMyComment('');
      setReviewSuccess('Cảm ơn bạn đã đánh giá!');
      loadReviews(id);
    } catch (err: any) {
      setReviewError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (!id) return;
    await api.reviews.delete(reviewId);
    loadReviews(id);
  };

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

      {/* ===== REVIEW SECTION ===== */}
      <div className="mt-16">
        <div className="flex items-center gap-4 mb-8">
          <h2 className="text-2xl font-extrabold text-gray-900">Đánh giá sách</h2>
          {avgRating && (
            <div className="flex items-center gap-2 bg-yellow-50 px-3 py-1 rounded-full">
              <StarRating value={Math.round(avgRating)} />
              <span className="font-bold text-yellow-600">{avgRating.toFixed(1)}</span>
              <span className="text-sm text-gray-500">({reviews.length} đánh giá)</span>
            </div>
          )}
        </div>

        {/* Form viết đánh giá */}
        {user ? (
          <form onSubmit={handleSubmitReview} className="bg-gray-50 rounded-2xl p-6 mb-8 space-y-4">
            <h3 className="font-bold text-gray-800">Viết đánh giá của bạn</h3>
            <div>
              <label className="text-sm font-medium text-gray-600 mb-2 block">Điểm đánh giá</label>
              <StarRating value={myRating} onChange={setMyRating} />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600 mb-2 block">Nhận xét</label>
              <textarea
                required
                value={myComment}
                onChange={e => setMyComment(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                placeholder="Chia sẻ cảm nhận của bạn về cuốn sách này..."
              />
            </div>
            {reviewError && <p className="text-red-500 text-sm">{reviewError}</p>}
            {reviewSuccess && <p className="text-green-600 text-sm">{reviewSuccess}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold hover:bg-indigo-700 transition-all disabled:opacity-50"
            >
              {submitting ? 'Đang gửi...' : 'Gửi đánh giá'}
            </button>
          </form>
        ) : (
          <p className="text-sm text-gray-500 mb-8 bg-gray-50 px-4 py-3 rounded-xl">
            <a href="/login" className="text-indigo-600 font-bold hover:underline">Đăng nhập</a> để viết đánh giá.
          </p>
        )}

        {/* Danh sách reviews */}
        {reviews.length === 0 ? (
          <p className="text-gray-400 text-sm">Chưa có đánh giá nào. Hãy là người đầu tiên!</p>
        ) : (
          <div className="space-y-4">
            {reviews.map(r => (
              <div key={r.id} className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-bold text-gray-800">{r.customer_name}</span>
                      <StarRating value={r.rating} />
                      <span className="text-xs text-gray-400">{new Date(r.created_at).toLocaleDateString('vi-VN')}</span>
                    </div>
                    <p className="text-gray-700 text-sm">{r.comment}</p>
                    {r.admin_reply && (
                      <div className="mt-3 pl-4 border-l-2 border-indigo-200 bg-indigo-50 rounded-r-xl py-2 pr-3">
                        <p className="text-xs font-bold text-indigo-600 mb-1">Phản hồi từ nhà sách</p>
                        <p className="text-sm text-gray-700">{r.admin_reply}</p>
                      </div>
                    )}
                  </div>
                  {user && (user.role === 'admin' || user.id === r.customer_id) && (
                    <button
                      onClick={() => handleDeleteReview(r.id)}
                      className="text-xs text-red-400 hover:text-red-600 shrink-0"
                    >
                      Xóa
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
