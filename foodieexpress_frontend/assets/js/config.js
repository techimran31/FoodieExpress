// FoodieExpress — Configuration & Constants
export const CONFIG = {
  APP_NAME: 'FoodieExpress',
  CURRENCY: '₹',
  CURRENCY_LOCALE: 'en-IN',
  DELIVERY_FEE: 25,
  STORAGE_KEYS: {
    CART: 'fe_cart',
    ORDERS: 'fe_orders',
    ACTIVE_ORDER: 'fe_active_order',
    USER: 'fe_user',
  },
  ORDER_STATUSES: ['Confirmed', 'Preparing', 'Picked up', 'Out for delivery', 'Delivered', 'Cancelled'],
  // Future: API base URL for backend integration
  API_BASE_URL: '',
};

export const money = (n) => `${CONFIG.CURRENCY}${Number(n).toLocaleString(CONFIG.CURRENCY_LOCALE)}`;

export const storage = {
  get(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || '[]');
    } catch {
      return [];
    }
  },
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  },
  remove(key) {
    localStorage.removeItem(key);
  },
};