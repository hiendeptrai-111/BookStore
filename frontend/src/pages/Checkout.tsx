import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../AppContext';
import { formatCurrency } from '../types';
import { CreditCard, MapPin, Phone, User, Tag, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../services/api';

export const Checkout: React.FC = () => {
  const { cart, user, clearCart } = useApp();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    address: '',
    phone: '',
    name: user?.name || '',
  });
  const [couponInput, setCouponInput] = useState('');
  const [couponLoading, setCouponLoading] = useState(false);
  const [couponState, setCouponState] = useState<{
    applied: boolean;
    discount: number;
    message: string;
    code: string;
  }>({ applied: false, discount: 0, message: '', code: '' });

  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const discount = couponState.applied ? couponState.discount : 0;
  const discountedSubtotal = subtotal - discount;
  const shipping = discountedSubtotal > 500000 ? 0 : 30000;
  const total = discountedSubtotal + shipping;

  const handleApplyCoupon = async () => {
    if (!couponInput.trim()) return;
    setCouponLoading(true);
    try {
      const res = await api.coupons.validate(couponInput.trim(), subtotal);
      if (res.valid) {
        setCouponState({ applied: true, discount: res.discount_amount, message: res.message, code: couponInput.trim().toUpperCase() });
      } else {
        setCouponState({ applied: false, discount: 0, message: res.message, code: '' });
      }
    } catch (err: any) {
      setCouponState({ applied: false, discount: 0, message: err.message || 'Mã không hợp lệ', code: '' });
    } finally {
      setCouponLoading(false);
    }
  };

  const handleRemoveCoupon = () => {
    setCouponState({ applied: false, discount: 0, message: '', code: '' });
    setCouponInput('');
  };

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!user) { navigate('/login'); return; }
    setLoading(true);
    try {
      const data = await api.orders.create({
        user_id: user.id,
        items: cart,
        total_price: total,
        address: formData.address,
        phone: formData.phone,
        coupon_code: couponState.applied ? couponState.code : '',
      });
      if (data.success) { clearCart(); navigate('/orders'); }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-10">Thanh toán</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="bg-white p-8 rounded-3xl border border-gray-100 space-y-6">
            <h3 className="text-xl font-bold text-gray-900">Thông tin giao hàng</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="checkout-name" className="block text-sm font-medium text-gray-700 mb-2">Họ và tên</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    id="checkout-name"
                    required
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="checkout-phone" className="block text-sm font-medium text-gray-700 mb-2">Số điện thoại</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    id="checkout-phone"
                    required
                    type="tel"
                    value={formData.phone}
                    onChange={e => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="checkout-address" className="block text-sm font-medium text-gray-700 mb-2">Địa chỉ nhận hàng</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <textarea
                    id="checkout-address"
                    required
                    rows={3}
                    value={formData.address}
                    onChange={e => setFormData({ ...formData, address: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-gray-100 space-y-4">
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Tag className="w-5 h-5 text-indigo-500" /> Mã giảm giá
            </h3>

            {couponState.applied ? (
              <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="text-sm font-bold text-green-700">{couponState.code}</p>
                    <p className="text-xs text-green-600">{couponState.message}</p>
                  </div>
                </div>
                <button type="button" onClick={handleRemoveCoupon}>
                  <XCircle className="w-5 h-5 text-gray-400 hover:text-red-500 transition-colors" />
                </button>
              </div>
            ) : (
              <>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={couponInput}
                    onChange={e => setCouponInput(e.target.value.toUpperCase())}
                    onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), handleApplyCoupon())}
                    placeholder="Nhập mã giảm giá..."
                    className="flex-1 px-4 py-3 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 uppercase"
                  />
                  <button
                    type="button"
                    onClick={handleApplyCoupon}
                    disabled={couponLoading || !couponInput.trim()}
                    className="px-5 py-3 bg-indigo-600 text-white rounded-xl font-bold text-sm hover:bg-indigo-700 transition-all disabled:opacity-50"
                  >
                    {couponLoading ? '...' : 'Áp dụng'}
                  </button>
                </div>
                {couponState.message && (
                  <p className="text-sm text-red-500 flex items-center gap-1">
                    <XCircle className="w-4 h-4" /> {couponState.message}
                  </p>
                )}
              </>
            )}
          </div>

          <div className="bg-white p-8 rounded-3xl border border-gray-100 space-y-6">
            <h3 className="text-xl font-bold text-gray-900">Phương thức thanh toán</h3>
            <div className="flex items-center p-4 border-2 border-indigo-600 rounded-2xl bg-indigo-50">
              <CreditCard className="w-6 h-6 text-indigo-600 mr-4" />
              <div>
                <p className="font-bold text-gray-900">Thanh toán khi nhận hàng (COD)</p>
                <p className="text-xs text-gray-500">Thanh toán bằng tiền mặt khi shipper giao hàng</p>
              </div>
            </div>
          </div>

          <button
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 disabled:opacity-50"
          >
            {loading ? 'Đang xử lý...' : 'Xác nhận đặt hàng'}
          </button>
        </form>

        <div className="space-y-6">
          <div className="bg-gray-50 p-8 rounded-3xl space-y-6">
            <h3 className="text-xl font-bold text-gray-900">Đơn hàng của bạn</h3>
            <div className="max-h-96 overflow-y-auto space-y-4 pr-2">
              {cart.map(item => (
                <div key={item.id} className="flex justify-between items-center">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-16 bg-gray-200 rounded-lg overflow-hidden">
                      <img src={item.image_url} alt={item.title} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900 truncate w-40">{item.title}</p>
                      <p className="text-xs text-gray-500">x{item.quantity}</p>
                    </div>
                  </div>
                  <span className="text-sm font-bold text-gray-900">{formatCurrency(item.price * item.quantity)}</span>
                </div>
              ))}
            </div>
            <div className="pt-6 border-t border-gray-200 space-y-4">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Tạm tính</span>
                <span>{formatCurrency(subtotal)}</span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between text-sm text-green-600 font-bold">
                  <span>Giảm giá ({couponState.code})</span>
                  <span>-{formatCurrency(discount)}</span>
                </div>
              )}
              <div className="flex justify-between text-sm text-gray-600">
                <span>Phí vận chuyển</span>
                <span>{shipping === 0 ? 'Miễn phí' : formatCurrency(shipping)}</span>
              </div>
              <div className="pt-4 border-t border-gray-200 flex justify-between text-lg font-bold text-gray-900">
                <span>Tổng cộng</span>
                <span>{formatCurrency(total)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
