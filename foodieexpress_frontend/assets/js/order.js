// FoodieExpress — Order Logic
import { CONFIG, storage } from './config.js';
import { cart } from './cart.js';

class OrderManager {
  constructor() {
    this.orders = storage.get(CONFIG.STORAGE_KEYS.ORDERS);
    this._simulationTimers = new Map();
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
    this.startDeliverySimulation(order.id);
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
    const order = this.find(id);
    if (!order) return false;
    this._stopSimulation(id);
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

  // ---- Delivery simulation (demo only) ----
  startDeliverySimulation(orderId) {
    this._stopSimulation(orderId);
    const order = this.find(orderId);
    if (!order || order.status === 'Delivered' || order.status === 'Cancelled') return;

    const statuses = CONFIG.ORDER_STATUSES.slice(0, 5); // Confirmed..Delivered
    const currentIdx = statuses.indexOf(order.status);
    if (currentIdx < 0 || currentIdx >= statuses.length - 1) return;

    const delays = [90, 90, 90, 90]; // seconds between status changes
    let idx = currentIdx;

    const timer = setInterval(() => {
      idx += 1;
      if (idx >= statuses.length) {
        this._stopSimulation(orderId);
        return;
      }
      this.updateStatus(orderId, statuses[idx]);
      if (statuses[idx] === 'Delivered' || statuses[idx] === 'Cancelled') {
        this._stopSimulation(orderId);
      }
    }, delays[idx - 1] * 1000);

    this._simulationTimers.set(orderId, timer);
  }

  _stopSimulation(orderId) {
    const timer = this._simulationTimers.get(orderId);
    if (timer) {
      clearInterval(timer);
      this._simulationTimers.delete(orderId);
    }
  }

  stopAllSimulations() {
    this._simulationTimers.forEach((timer, id) => clearInterval(timer));
    this._simulationTimers.clear();
  }

  // ---- Reorder ----
  reorder(orderId) {
    const order = this.find(orderId);
    if (!order || !order.items || !order.items.length) return false;

    // Clear cart and add all items from the order
    cart.items = [];
    order.items.forEach((item) => {
      cart.items.push({
        restaurantId: item.restaurantId,
        restaurant: item.restaurant,
        name: item.name,
        price: item.price,
        emoji: item.emoji,
        qty: item.qty,
      });
    });
    cart.save();
    return true;
  }
}

export const orderManager = new OrderManager();