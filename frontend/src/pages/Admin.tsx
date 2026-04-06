import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../AppContext';
import { LayoutDashboard, Book, ShoppingBag, Users, TrendingUp, Package, DollarSign, UserCheck } from 'lucide-react';
import { formatCurrency } from '../types';
import { api } from '../services/api';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState({
    revenue: 0, orders: 0, users: 0, books: 0,
    recent_orders: [] as any[],
    low_stock: 0, in_stock: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.admin.getStats()
      .then(data => { setStats(data); setLoading(false); })
      .catch(err => { console.error(err); setLoading(false); });
  }, []);

  const cards = [
    { title: 'Doanh thu', value: formatCurrency(stats.revenue), icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
    { title: 'Đơn hàng', value: stats.orders, icon: ShoppingBag, color: 'text-blue-600', bg: 'bg-blue-50' },
    { title: 'Người dùng', value: stats.users, icon: Users, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Đầu sách', value: stats.books, icon: Book, color: 'text-orange-600', bg: 'bg-orange-50' },
  ];

  const statusLabel: Record<string, string> = {
    pending: 'Chờ xác nhận',
    confirmed: 'Xác nhận',
    shipped: 'Đang giao',
    delivered: 'Đã giao',
    cancelled: 'Đã hủy',
  };

  const statusColor: Record<string, string> = {
    pending: 'bg-yellow-50 text-yellow-600',
    confirmed: 'bg-blue-50 text-blue-600',
    shipped: 'bg-indigo-50 text-indigo-600',
    delivered: 'bg-green-50 text-green-600',
    cancelled: 'bg-red-50 text-red-600',
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-gray-400 text-sm">Đang tải dữ liệu...</div>
    </div>
  );

  return (
    <div className="space-y-10">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tổng quan hệ thống</h1>
        <div className="text-sm text-gray-500">Cập nhật lần cuối: {new Date().toLocaleTimeString()}</div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, i) => (
          <div key={i} className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
            <div className={`${card.bg} w-12 h-12 rounded-2xl flex items-center justify-center mb-6`}>
              <card.icon className={`w-6 h-6 ${card.color}`} />
            </div>
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">{card.title}</p>
            <p className="text-2xl font-extrabold text-gray-900">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Đơn hàng gần đây - từ database thật */}
        <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" /> Đơn hàng gần đây
          </h3>
          {stats.recent_orders.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-8">Chưa có đơn hàng nào</p>
          ) : (
            <div className="space-y-4">
              {stats.recent_orders.map((order: any) => (
                <div key={order.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 rounded-full bg-indigo-600 flex-shrink-0"></div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">
                        #{order.id} — {order.customer_name}
                      </p>
                      <p className="text-xs text-gray-400">{order.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-indigo-600">{formatCurrency(order.total)}</span>
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${statusColor[order.status] || 'bg-gray-50 text-gray-600'}`}>
                      {statusLabel[order.status] || order.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Trạng thái kho - từ database thật */}
        <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Package className="w-5 h-5 mr-2 text-indigo-600" /> Trạng thái kho
          </h3>
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm font-bold text-gray-700">Sách sắp hết hàng</p>
                <p className="text-xs text-gray-400">Còn dưới 10 cuốn trong kho</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${stats.low_stock > 0 ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                {stats.low_stock} đầu sách
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-red-400 h-2 rounded-full transition-all"
                style={{ width: stats.books > 0 ? `${(stats.low_stock / stats.books) * 100}%` : '0%' }}
              />
            </div>

            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm font-bold text-gray-700">Sách còn hàng tốt</p>
                <p className="text-xs text-gray-400">Từ 10 cuốn trở lên</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-50 text-green-600">
                {stats.in_stock} đầu sách
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-green-400 h-2 rounded-full transition-all"
                style={{ width: stats.books > 0 ? `${(stats.in_stock / stats.books) * 100}%` : '0%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const AdminBooks: React.FC = () => {
  const { token } = useApp();
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
  const [books, setBooks] = useState<any[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [currentBook, setCurrentBook] = useState<any>(null);
  const [authors, setAuthors] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [publishers, setPublishers] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api.books.getAll().then(setBooks).catch(console.error);
    fetch(`${import.meta.env.VITE_API_URL}/admin/authors/`, { headers: authHeaders }).then(r => r.json()).then(setAuthors);
    fetch(`${import.meta.env.VITE_API_URL}/admin/categories/`, { headers: authHeaders }).then(r => r.json()).then(setCategories);
    fetch(`${import.meta.env.VITE_API_URL}/admin/publishers/`, { headers: authHeaders }).then(r => r.json()).then(setPublishers);
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa sách này?')) {
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/admin/books/${id}/delete/`, { method: 'DELETE', headers: authHeaders });
        setBooks(books.filter(b => b.id !== id));
      } catch (err) { console.error(err); }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const payload = {
        title: currentBook.title,
        isbn: currentBook.isbn,
        author_id: currentBook.author_id,
        category_id: currentBook.category_id,
        publisher_id: currentBook.publisher_id,
        price: currentBook.price,
        stock_quantity: currentBook.stock_quantity,
        description: currentBook.description,
        image_url: currentBook.image_url,
      };

      const url = currentBook.book_id
        ? `${import.meta.env.VITE_API_URL}/admin/books/${currentBook.book_id}/`
        : `${import.meta.env.VITE_API_URL}/admin/books/`;
      const method = currentBook.book_id ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Lỗi không xác định');

      setIsEditing(false);
      api.books.getAll().then(setBooks);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quản lý sách</h1>
        <button
          onClick={() => { setCurrentBook({ title: '', isbn: '', author_id: '', category_id: '', publisher_id: '', price: 0, stock_quantity: 0, description: '', image_url: '' }); setIsEditing(true); setError(''); }}
          className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-700 transition-all"
        >
          Thêm sách mới
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Sách</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thể loại</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Giá</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Kho</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {books.map(book => (
              <tr key={book.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-4">
                    <img src={book.image_url || `https://picsum.photos/seed/book${book.id}/400/600`} className="w-10 h-14 object-cover rounded shadow-sm" referrerPolicy="no-referrer" />
                    <div>
                      <p className="font-bold text-gray-900">{book.title}</p>
                      <p className="text-xs text-gray-500">{book.author}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{book.category}</td>
                <td className="px-6 py-4 font-bold text-indigo-600">{formatCurrency(book.price)}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{book.stock}</td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button onClick={() => { setCurrentBook({...book, author_id: book.author, category_id: book.category, publisher_id: book.publisher, stock_quantity: book.stock }); setIsEditing(true); setError(''); }} className="text-blue-600 hover:underline text-sm font-bold">Sửa</button>
                    <button onClick={() => handleDelete(book.id)} className="text-red-600 hover:underline text-sm font-bold">Xóa</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isEditing && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white w-full max-w-2xl rounded-3xl p-8 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">{currentBook.book_id ? 'Sửa sách' : 'Thêm sách mới'}</h2>
            {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-xl mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">Tiêu đề</label>
                <input required value={currentBook.title} onChange={e => setCurrentBook({...currentBook, title: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">ISBN</label>
                <input required value={currentBook.isbn || ''} onChange={e => setCurrentBook({...currentBook, isbn: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" placeholder="978-xxx-xxx-xxx" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tác giả</label>
                <select required value={currentBook.author_id || ''} onChange={e => setCurrentBook({...currentBook, author_id: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl">
                  <option value="">-- Chọn tác giả --</option>
                  {authors.map(a => <option key={a.author_id} value={a.author_id}>{a.full_name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Thể loại</label>
                <select required value={currentBook.category_id || ''} onChange={e => setCurrentBook({...currentBook, category_id: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl">
                  <option value="">-- Chọn thể loại --</option>
                  {categories.map(c => <option key={c.category_id} value={c.category_id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Nhà xuất bản</label>
                <select required value={currentBook.publisher_id || ''} onChange={e => setCurrentBook({...currentBook, publisher_id: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl">
                  <option value="">-- Chọn NXB --</option>
                  {publishers.map(p => <option key={p.publisher_id} value={p.publisher_id}>{p.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Giá</label>
                <input required type="number" value={currentBook.price} onChange={e => setCurrentBook({...currentBook, price: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Số lượng kho</label>
                <input required type="number" value={currentBook.stock_quantity} onChange={e => setCurrentBook({...currentBook, stock_quantity: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">URL Hình ảnh</label>
                <input value={currentBook.image_url || ''} onChange={e => setCurrentBook({...currentBook, image_url: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" placeholder="https://..." />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">Mô tả</label>
                <textarea rows={4} value={currentBook.description || ''} onChange={e => setCurrentBook({...currentBook, description: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl"></textarea>
              </div>
              <div className="md:col-span-2 flex justify-end space-x-4 pt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 text-gray-500 font-bold">Hủy</button>
                <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold">Lưu thay đổi</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export const AdminOrders: React.FC = () => {
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    api.orders.getAll().then(setOrders).catch(err => console.error(err));
  }, []);

  const updateStatus = async (id: number, status: string) => {
    try {
      await api.orders.updateStatus(id, status);
      api.orders.getAll().then(setOrders);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Quản lý đơn hàng</h1>
      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Mã đơn</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Khách hàng</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Tổng tiền</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Trạng thái</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {orders.map(order => (
              <tr key={order.id}>
                <td className="px-6 py-4 font-bold text-gray-900">#{order.id}</td>
                <td className="px-6 py-4">
                  <p className="text-sm font-bold text-gray-900">{order.user_name}</p>
                  <p className="text-xs text-gray-500">{order.phone}</p>
                </td>
                <td className="px-6 py-4 font-bold text-indigo-600">{formatCurrency(order.total_price)}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    order.status === 'delivered' ? 'bg-green-50 text-green-600' :
                    order.status === 'cancelled' ? 'bg-red-50 text-red-600' :
                    'bg-orange-50 text-orange-600'
                  }`}>
                    {order.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <select 
                    value={order.status}
                    onChange={(e) => updateStatus(order.id, e.target.value)}
                    className="text-xs font-bold border-none bg-gray-50 rounded-lg p-1"
                  >
                    <option value="pending">Chờ xác nhận</option>
                    <option value="confirmed">Xác nhận</option>
                    <option value="shipped">Đang giao</option>
                    <option value="delivered">Đã giao</option>
                    <option value="cancelled">Hủy đơn</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    api.admin.getUsers().then(setUsers).catch(err => console.error(err));
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Quản lý người dùng</h1>
      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Tên</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Email</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Vai trò</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map(user => (
              <tr key={user.id}>
                <td className="px-6 py-4 text-sm text-gray-500">#{user.id}</td>
                <td className="px-6 py-4 font-bold text-gray-900">{user.name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${user.role === 'admin' ? 'bg-purple-50 text-purple-600' : 'bg-gray-50 text-gray-600'}`}>
                    {user.role}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const AdminAuthors: React.FC = () => {
  const [authors, setAuthors] = useState<any[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [current, setCurrent] = useState<any>(null);
  const [error, setError] = useState('');
  const API = import.meta.env.VITE_API_URL;

  const load = () => fetch(`${API}/admin/authors/`, { headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` } }).then(r => r.json()).then(setAuthors);
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const url = current.author_id
        ? `${API}/admin/authors/${current.author_id}/`
        : `${API}/admin/authors/create/`;
      const method = current.author_id ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
        body: JSON.stringify(current)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setIsEditing(false);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Xóa tác giả này?')) return;
    try {
      const res = await fetch(`${API}/admin/authors/${id}/delete/`, { method: 'DELETE', headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      load();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quản lý tác giả</h1>
        <button
          onClick={() => { setCurrent({ full_name: '', bio: '', nationality: '' }); setIsEditing(true); setError(''); }}
          className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-700 transition-all"
        >
          Thêm tác giả
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Tên tác giả</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Quốc tịch</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {authors.map(a => (
              <tr key={a.author_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-500">#{a.author_id}</td>
                <td className="px-6 py-4 font-bold text-gray-900">{a.full_name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{a.nationality || '—'}</td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button onClick={() => { setCurrent(a); setIsEditing(true); setError(''); }} className="text-blue-600 hover:underline text-sm font-bold">Sửa</button>
                    <button onClick={() => handleDelete(a.author_id)} className="text-red-600 hover:underline text-sm font-bold">Xóa</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isEditing && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white w-full max-w-lg rounded-3xl p-8">
            <h2 className="text-2xl font-bold mb-6">{current.author_id ? 'Sửa tác giả' : 'Thêm tác giả'}</h2>
            {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-xl mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tên tác giả</label>
                <input required value={current.full_name} onChange={e => setCurrent({...current, full_name: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Quốc tịch</label>
                <input value={current.nationality || ''} onChange={e => setCurrent({...current, nationality: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tiểu sử</label>
                <textarea rows={3} value={current.bio || ''} onChange={e => setCurrent({...current, bio: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl"></textarea>
              </div>
              <div className="flex justify-end space-x-4 pt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 text-gray-500 font-bold">Hủy</button>
                <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold">Lưu</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export const AdminCategories: React.FC = () => {
  const [categories, setCategories] = useState<any[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [current, setCurrent] = useState<any>(null);
  const [error, setError] = useState('');
  const API = import.meta.env.VITE_API_URL;

  const load = () => fetch(`${API}/admin/categories/`, { headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` } }).then(r => r.json()).then(setCategories);
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const url = current.category_id
        ? `${API}/admin/categories/${current.category_id}/`
        : `${API}/admin/categories/create/`;
      const method = current.category_id ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
        body: JSON.stringify(current)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setIsEditing(false);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Xóa danh mục này?')) return;
    try {
      const res = await fetch(`${API}/admin/categories/${id}/delete/`, { method: 'DELETE', headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      load();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quản lý danh mục</h1>
        <button
          onClick={() => { setCurrent({ name: '' }); setIsEditing(true); setError(''); }}
          className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-700 transition-all"
        >
          Thêm danh mục
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Tên danh mục</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {categories.map(c => (
              <tr key={c.category_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-500">#{c.category_id}</td>
                <td className="px-6 py-4 font-bold text-gray-900">{c.name}</td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button onClick={() => { setCurrent(c); setIsEditing(true); setError(''); }} className="text-blue-600 hover:underline text-sm font-bold">Sửa</button>
                    <button onClick={() => handleDelete(c.category_id)} className="text-red-600 hover:underline text-sm font-bold">Xóa</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isEditing && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white w-full max-w-md rounded-3xl p-8">
            <h2 className="text-2xl font-bold mb-6">{current.category_id ? 'Sửa danh mục' : 'Thêm danh mục'}</h2>
            {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-xl mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tên danh mục</label>
                <input required value={current.name} onChange={e => setCurrent({...current, name: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div className="flex justify-end space-x-4 pt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 text-gray-500 font-bold">Hủy</button>
                <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold">Lưu</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};