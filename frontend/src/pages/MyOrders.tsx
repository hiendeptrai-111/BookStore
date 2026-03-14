import React, { useEffect, useState } from 'react';
import { useApp } from '../AppContext';
import { Order, formatCurrency } from '../types';
import { Package, Clock, CheckCircle, Truck, XCircle } from 'lucide-react';
import { format } from 'date-fns';
import { vi } from 'date-fns/locale';
import { api } from '../services/api';

export const MyOrders: React.FC = () => {
  const { user } = useApp();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      api.orders.getUserOrders(user.id)
        .then(data => {
          setOrders(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [user]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-5 h-5 text-orange-500" />;
      case 'confirmed': return <CheckCircle className="w-5 h-5 text-blue-500" />;
      case 'shipped': return <Truck className="w-5 h-5 text-indigo-500" />;
      case 'delivered': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return <Package className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Chờ xác nhận';
      case 'confirmed': return 'Đã xác nhận';
      case 'shipped': return 'Đang giao hàng';
      case 'delivered': return 'Đã giao hàng';
      case 'cancelled': return 'Đã hủy';
      default: return status;
    }
  };

  if (loading) return <div className="p-20 text-center">Đang tải đơn hàng...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-10">Đơn hàng của tôi</h1>

      {orders.length === 0 ? (
        <div className="bg-white p-12 rounded-3xl border border-gray-100 text-center">
          <Package className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">Bạn chưa có đơn hàng nào.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map(order => (
            <div key={order.id} className="bg-white p-8 rounded-3xl border border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-2">
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Mã đơn: #{order.id}</span>
                  <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-gray-50">
                    {getStatusIcon(order.status)}
                    <span className="text-xs font-bold text-gray-700">{getStatusText(order.status)}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-500">
                  Ngày đặt: {format(new Date(order.created_at), 'PPP', { locale: vi })}
                </p>
                <p className="text-sm text-gray-600 truncate max-w-md">Địa chỉ: {order.address}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400 uppercase font-bold tracking-widest mb-1">Tổng tiền</p>
                <p className="text-2xl font-extrabold text-indigo-600">{formatCurrency(order.total_price)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
