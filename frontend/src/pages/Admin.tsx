import React, { useEffect, useState } from 'react';
import { Book, ShoppingBag, Users, TrendingUp, Package, DollarSign } from 'lucide-react';
import { formatCurrency } from '../types';
import { api } from '../services/api';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState({
    revenue: 0,
    orders: 0,
    users: 0,
    books: 0,
    recent_orders: [] as any[],
    low_stock: 0,
    in_stock: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.admin.getStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const cards = [
    { title: 'Doanh thu', value: formatCurrency(stats.revenue), icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
    { title: 'Don hang', value: stats.orders, icon: ShoppingBag, color: 'text-blue-600', bg: 'bg-blue-50' },
    { title: 'Nguoi dung', value: stats.users, icon: Users, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Dau sach', value: stats.books, icon: Book, color: 'text-orange-600', bg: 'bg-orange-50' },
  ];

  const statusLabel: Record<string, string> = {
    pending: 'Cho xac nhan',
    confirmed: 'Xac nhan',
    shipped: 'Dang giao',
    delivered: 'Da giao',
    cancelled: 'Da huy',
  };

  const statusColor: Record<string, string> = {
    pending: 'bg-yellow-50 text-yellow-600',
    confirmed: 'bg-blue-50 text-blue-600',
    shipped: 'bg-indigo-50 text-indigo-600',
    delivered: 'bg-green-50 text-green-600',
    cancelled: 'bg-red-50 text-red-600',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 text-sm">Dang tai du lieu...</div>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tong quan he thong</h1>
        <div className="text-sm text-gray-500">Cap nhat lan cuoi: {new Date().toLocaleTimeString()}</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, index) => (
          <div key={index} className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
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
            <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" /> Don hang gan day
          </h3>
          {stats.recent_orders.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-8">Chua co don hang nao</p>
          ) : (
            <div className="space-y-4">
              {stats.recent_orders.map((order: any) => (
                <div key={order.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 rounded-full bg-indigo-600 flex-shrink-0"></div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">#{order.id} - {order.customer_name}</p>
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

        <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Package className="w-5 h-5 mr-2 text-indigo-600" /> Trang thai kho
          </h3>
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm font-bold text-gray-700">Sach sap het hang</p>
                <p className="text-xs text-gray-400">Con duoi 10 cuon trong kho</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${stats.low_stock > 0 ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                {stats.low_stock} dau sach
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
                <p className="text-sm font-bold text-gray-700">Sach con hang tot</p>
                <p className="text-xs text-gray-400">Tu 10 cuon tro len</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-50 text-green-600">
                {stats.in_stock} dau sach
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
  const [books, setBooks] = useState<any[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [currentBook, setCurrentBook] = useState<any>(null);
  const [authors, setAuthors] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [publishers, setPublishers] = useState<any[]>([]);
  const [error, setError] = useState('');

  const loadBooks = () => api.books.getAll().then(setBooks).catch(console.error);

  useEffect(() => {
    loadBooks();
    api.admin.getAuthors().then(setAuthors).catch(console.error);
    api.admin.getCategories().then(setCategories).catch(console.error);
    api.admin.getPublishers().then(setPublishers).catch(console.error);
  }, []);

  const openCreateModal = () => {
    setCurrentBook({
      title: '',
      isbn: '',
      author_id: '',
      category_id: '',
      publisher_id: '',
      price: 0,
      stock_quantity: 0,
      description: '',
      image_url: '',
    });
    setError('');
    setIsEditing(true);
  };

  const openEditModal = (book: any) => {
    setCurrentBook({
      ...book,
      author_id: book.author_id,
      category_id: book.category_id,
      publisher_id: book.publisher_id,
      stock_quantity: book.stock,
    });
    setError('');
    setIsEditing(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Ban co chac chan muon xoa sach nay?')) return;

    try {
      await api.books.delete(id);
      setBooks(prev => prev.filter(book => book.id !== id));
    } catch (err) {
      console.error(err);
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

      if (currentBook.book_id) {
        await api.books.update(currentBook.book_id, payload);
      } else {
        await api.books.create(payload);
      }

      setIsEditing(false);
      await loadBooks();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quan ly sach</h1>
        <button
          onClick={openCreateModal}
          className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-700 transition-all"
        >
          Them sach moi
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Sach</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">The loai</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Gia</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Kho</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tac</th>
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
                    <button onClick={() => openEditModal(book)} className="text-blue-600 hover:underline text-sm font-bold">Sua</button>
                    <button onClick={() => handleDelete(book.id)} className="text-red-600 hover:underline text-sm font-bold">Xoa</button>
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
            <h2 className="text-2xl font-bold mb-6">{currentBook.book_id ? 'Sua sach' : 'Them sach moi'}</h2>
            {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-xl mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">Tieu de</label>
                <input required value={currentBook.title} onChange={e => setCurrentBook({...currentBook, title: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">ISBN</label>
                <input required value={currentBook.isbn || ''} onChange={e => setCurrentBook({...currentBook, isbn: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" placeholder="978-xxx-xxx-xxx" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tac gia</label>
                <select required value={currentBook.author_id || ''} onChange={e => setCurrentBook({...currentBook, author_id: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl">
                  <option value="">-- Chon tac gia --</option>
                  {authors.map(author => <option key={author.author_id} value={author.author_id}>{author.full_name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">The loai</label>
                <select required value={currentBook.category_id || ''} onChange={e => setCurrentBook({...currentBook, category_id: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl">
                  <option value="">-- Chon the loai --</option>
                  {categories.map(category => <option key={category.category_id} value={category.category_id}>{category.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Nha xuat ban</label>
                <select required value={currentBook.publisher_id || ''} onChange={e => setCurrentBook({...currentBook, publisher_id: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl">
                  <option value="">-- Chon NXB --</option>
                  {publishers.map(publisher => <option key={publisher.publisher_id} value={publisher.publisher_id}>{publisher.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Gia</label>
                <input required type="number" value={currentBook.price} onChange={e => setCurrentBook({...currentBook, price: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">So luong kho</label>
                <input required type="number" value={currentBook.stock_quantity} onChange={e => setCurrentBook({...currentBook, stock_quantity: Number(e.target.value)})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">URL hinh anh</label>
                <input value={currentBook.image_url || ''} onChange={e => setCurrentBook({...currentBook, image_url: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" placeholder="https://..." />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-bold text-gray-700 mb-2">Mo ta</label>
                <textarea rows={4} value={currentBook.description || ''} onChange={e => setCurrentBook({...currentBook, description: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl"></textarea>
              </div>
              <div className="md:col-span-2 flex justify-end space-x-4 pt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 text-gray-500 font-bold">Huy</button>
                <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold">Luu thay doi</button>
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
      <h1 className="text-3xl font-bold text-gray-900">Quan ly don hang</h1>
      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Ma don</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Khach hang</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Tong tien</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Trang thai</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tac</th>
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
                    onChange={e => updateStatus(order.id, e.target.value)}
                    className="text-xs font-bold border-none bg-gray-50 rounded-lg p-1"
                  >
                    <option value="pending">Cho xac nhan</option>
                    <option value="confirmed">Xac nhan</option>
                    <option value="shipped">Dang giao</option>
                    <option value="delivered">Da giao</option>
                    <option value="cancelled">Huy don</option>
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
      <h1 className="text-3xl font-bold text-gray-900">Quan ly nguoi dung</h1>
      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Ten</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Email</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Vai tro</th>
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
  const load = () => api.admin.getAuthors().then(setAuthors);

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (current.author_id) {
        await api.admin.updateAuthor(current.author_id, current);
      } else {
        await api.admin.createAuthor(current);
      }
      setIsEditing(false);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Xoa tac gia nay?')) return;
    try {
      await api.admin.deleteAuthor(id);
      load();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quan ly tac gia</h1>
        <button
          onClick={() => { setCurrent({ full_name: '', bio: '', nationality: '' }); setIsEditing(true); setError(''); }}
          className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-700 transition-all"
        >
          Them tac gia
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Ten tac gia</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Quoc tich</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tac</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {authors.map(author => (
              <tr key={author.author_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-500">#{author.author_id}</td>
                <td className="px-6 py-4 font-bold text-gray-900">{author.full_name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{author.nationality || '-'}</td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button onClick={() => { setCurrent(author); setIsEditing(true); setError(''); }} className="text-blue-600 hover:underline text-sm font-bold">Sua</button>
                    <button onClick={() => handleDelete(author.author_id)} className="text-red-600 hover:underline text-sm font-bold">Xoa</button>
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
            <h2 className="text-2xl font-bold mb-6">{current.author_id ? 'Sua tac gia' : 'Them tac gia'}</h2>
            {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-xl mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Ten tac gia</label>
                <input required value={current.full_name} onChange={e => setCurrent({...current, full_name: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Quoc tich</label>
                <input value={current.nationality || ''} onChange={e => setCurrent({...current, nationality: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Tieu su</label>
                <textarea rows={3} value={current.bio || ''} onChange={e => setCurrent({...current, bio: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl"></textarea>
              </div>
              <div className="flex justify-end space-x-4 pt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 text-gray-500 font-bold">Huy</button>
                <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold">Luu</button>
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
  const load = () => api.admin.getCategories().then(setCategories);

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (current.category_id) {
        await api.admin.updateCategory(current.category_id, current);
      } else {
        await api.admin.createCategory(current);
      }
      setIsEditing(false);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Xoa danh muc nay?')) return;
    try {
      await api.admin.deleteCategory(id);
      load();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Quan ly danh muc</h1>
        <button
          onClick={() => { setCurrent({ name: '' }); setIsEditing(true); setError(''); }}
          className="bg-indigo-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-indigo-700 transition-all"
        >
          Them danh muc
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Ten danh muc</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Thao tac</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {categories.map(category => (
              <tr key={category.category_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-500">#{category.category_id}</td>
                <td className="px-6 py-4 font-bold text-gray-900">{category.name}</td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button onClick={() => { setCurrent(category); setIsEditing(true); setError(''); }} className="text-blue-600 hover:underline text-sm font-bold">Sua</button>
                    <button onClick={() => handleDelete(category.category_id)} className="text-red-600 hover:underline text-sm font-bold">Xoa</button>
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
            <h2 className="text-2xl font-bold mb-6">{current.category_id ? 'Sua danh muc' : 'Them danh muc'}</h2>
            {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-xl mb-4">{error}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Ten danh muc</label>
                <input required value={current.name} onChange={e => setCurrent({...current, name: e.target.value})} className="w-full px-4 py-3 bg-gray-50 border-none rounded-xl" />
              </div>
              <div className="flex justify-end space-x-4 pt-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 text-gray-500 font-bold">Huy</button>
                <button type="submit" className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold">Luu</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
