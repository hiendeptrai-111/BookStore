import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LayoutDashboard, Book, ShoppingBag, Users, TrendingUp, Package, DollarSign, UserCheck } from 'lucide-react';
import { formatCurrency } from '../types';
import { api } from '../services/api';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState({ revenue: 0, orders: 0, users: 0, books: 0 });

  useEffect(() => {
    api.admin.getStats().then(setStats).catch(err => console.error(err));
  }, []);

  const cards = [
    { title: 'Doanh thu', value: formatCurrency(stats.revenue), icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
    { title: 'Đơn hàng', value: stats.orders, icon: ShoppingBag, color: 'text-blue-600', bg: 'bg-blue-50' },
    { title: 'Người dùng', value: stats.users, icon: Users, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Đầu sách', value: stats.books, icon: Book, color: 'text-orange-600', bg: 'bg-orange-50' },
  ];

  return (
    <div className="space-y-10">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tổng quan hệ thống</h1>
        <div className="text-sm text-gray-500">Cập nhật lần cuối: {new Date().toLocaleTimeString()}</div>
      </div>

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
        <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" /> Hoạt động gần đây
          </h3>
          <div className="space-y-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex items-center space-x-4">
                <div className="w-2 h-2 rounded-full bg-indigo-600"></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900 font-medium">Đơn hàng mới #12{i} vừa được đặt</p>
                  <p className="text-xs text-gray-400">2 phút trước</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <UserCheck className="w-5 h-5 mr-2 text-indigo-600" /> Trạng thái kho
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Sách sắp hết hàng</span>
              <span className="px-2 py-1 bg-red-50 text-red-600 text-xs font-bold rounded">5 đầu sách</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Sách mới nhập</span>
              <span className="px-2 py-1 bg-green-50 text-green-600 text-xs font-bold rounded">12 đầu sách</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const AdminBooks: React.FC = () => {
  const [books, setBooks] = useState<any[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [currentBook, setCurrentBook] = useState<any>(null);

  useEffect(() => {
    api.books.getAll().then(setBooks).catch(err => console.error(err));
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa sách này?')) {
      try {
        await api.books.delete(id);
        setBooks(books.filter(b => b.id !== id));
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (currentBook.id) {
        await api.books.update(currentBook.id, currentBook);
      } else {
        await api.books.create(currentBook);
      }
      
      setIsEditing(false);
      api.books.getAll().then(setBooks);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quản lý sách</h1>
        <button 
          onClick={() => { setCurrentBook({ title: '', author: '', price: 0, description: '', image_url: '', category: '', stock: 0 }); setIsEditing(true); }}
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
                    <img src={book.image_url} className="w-10 h-14 object-cover rounded shadow-sm" referrerPolicy="no-referrer" />
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
                    <button onClick={() => { setCurrentBook(book); setIsEditing(true); }} className="text-blue-600 hover:underline text-sm font-bold">Sửa</button>
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
            <h2 className="text-2xl font-bold mb-6">{currentBook.id ? 'Sửa sách' : 'Thêm sách mới'}</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">Tiêu đề</label>
                <input required value={currentBook.title} onChange={e => setCurrentBook({...currentBook, title: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tác giả</label>
                <input required value={currentBook.author} onChange={e => setCurrentBook({...currentBook, author: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Thể loại</label>
                <input required value={currentBook.category} onChange={e => setCurrentBook({...currentBook, category: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Giá</label>
                <input required type="number" value={currentBook.price} onChange={e => setCurrentBook({...currentBook, price: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Số lượng kho</label>
                <input required type="number" value={currentBook.stock} onChange={e => setCurrentBook({...currentBook, stock: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">URL Hình ảnh</label>
                <input required value={currentBook.image_url} onChange={e => setCurrentBook({...currentBook, image_url: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">Mô tả</label>
                <textarea required rows={4} value={currentBook.description} onChange={e => setCurrentBook({...currentBook, description: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl"></textarea>
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
