// FoodieExpress — Order Logic
import { CONFIG, storage } from './config.js';
import { cart } from './cart.js';

class OrderManager {
  constructor() {
    this.orders = storage.get(CONFIG.STORAGE_KEYS.ORDERS);
  }

  save() {
    storage.set(CONFIG.STORAGE_KEYS.ORDERS, this.orders);
  }

  getAll() {
    return [...this.orders].reverse(); // newest first
  }

  find(id) {
    return this.orders.find((o) => o.id === id);
  }

  create(customer, paymentMethod) {
    if (cart.isEmpty()) {
      throw new Error('Cannot place order with empty cart');
    }

    const order = {
      id: `FE${Math.floor(100000 + Math.random() * 900000)}`,
      date: new Date().toISOString(),
      status: 'Confirmed',
      items: [...cart.items],
      total: cart.getTotal(),
      customer,
      payment: paymentMethod,
    };

    this.orders.unshift(order);
    this.save();
    storage.set(CONFIG.STORAGE_KEYS.ACTIVE_ORDER, order.id);
    cart.clear();
    return order;
  }

  updateStatus(id, status) {
    const order = this.find(id);
    if (!order) return false;
    if (!CONFIG.ORDER_STATUSES.includes(status)) return false;
    order.status = status;
    this.save();
    window.dispatchEvent(new CustomEvent('order:updated', { detail: { order } }));
    return true;
  }

  cancel(id) {
    return this.updateStatus(id, 'Cancelled');
  }

  getActiveId() {
    return storage.get(CONFIG.STORAGE_KEYS.ACTIVE_ORDER) || (this.orders[0]?.id || null);
  }

  setActiveId(id) {
    storage.set(CONFIG.STORAGE_KEYS.ACTIVE_ORDER, id);
  }

  getStats() {
    const all = this.orders;
    return {
      total: all.length,
      active: all.filter((o) => o.status !== 'Delivered' && o.status !== 'Cancelled').length,
      revenue: all
        .filter((o) => o.status !== 'Cancelled')
        .reduce((sum, o) => sum + o.total, 0),
    };
  }
}

export const orderManager = new OrderManager();