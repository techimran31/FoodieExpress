// FoodieExpress — API Service Layer
// Currently uses localStorage (demo mode).
// To connect a real backend, replace the methods below with fetch() calls
// to your API endpoints and set CONFIG.API_BASE_URL.

import { CONFIG } from './config.js';

const API = {
  // Restaurants
  async getRestaurants() {
    // Demo: return static data. Replace with:
    // const res = await fetch(`${CONFIG.API_BASE_URL}/restaurants`);
    // return res.json();
    return window.restaurants || [];
  },

  async getRestaurant(id) {
    // Demo: return static data
    return window.restaurants?.find((r) => r.id === id) || null;
  },

  async getMenu(restaurantId) {
    // Demo: return static data
    return window.menus?.[restaurantId] || [];
  },

  // Orders
  async getOrders() {
    // Demo: return from localStorage
    return JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.ORDERS) || '[]');
  },

  async createOrder(orderData) {
    // Demo: save to localStorage
    const orders = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.ORDERS) || '[]');
    orders.unshift(orderData);
    localStorage.setItem(CONFIG.STORAGE_KEYS.ORDERS, JSON.stringify(orders));
    return orderData;
  },

  async updateOrderStatus(id, status) {
    // Demo: update localStorage
    const orders = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.ORDERS) || '[]');
    const order = orders.find((o) => o.id === id);
    if (order) {
      order.status = status;
      localStorage.setItem(CONFIG.STORAGE_KEYS.ORDERS, JSON.stringify(orders));
    }
    return order;
  },
};

export default API;