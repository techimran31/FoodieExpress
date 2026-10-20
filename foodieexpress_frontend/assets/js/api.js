// ============================================================================
// FoodieExpress — api.js (API Service Layer)
// ----------------------------------------------------------------------------
// Single place where ALL data access happens.
// Currently "demo mode": reads/writes localStorage + static data.
// To connect a real backend:
//   1. Set CONFIG.API_BASE_URL in config.js
//   2. Replace each method body with fetch() to your endpoints
// Callers never change — they keep using API.getRestaurants() etc.
// ============================================================================

import { CONFIG } from './config.js';

const API = {
  // -------------------------------------------------------------------------
  // GET /restaurants — list all restaurants
  // Demo: returns the static array exposed on window by ui.js.
  // Real:  const res = await fetch(`${CONFIG.API_BASE_URL}/restaurants`);
  //        return res.json();
  // -------------------------------------------------------------------------
  async getRestaurants() {
    return window.restaurants || []; // [] if ui.js hasn't loaded yet
  },

  // GET /restaurants/:id — single restaurant by id (null if not found)
  async getRestaurant(id) {
    return window.restaurants?.find((r) => r.id === id) || null;
    //        ^ optional chaining: safe even if window.restaurants is undefined
  },

  // GET /restaurants/:id/menu — menu array for one restaurant
  async getMenu(restaurantId) {
    return window.menus?.[restaurantId] || [];
  },

  // -------------------------------------------------------------------------
  // GET /orders — all saved orders (newest first is handled by caller)
  // Demo: parse the JSON blob stored under the ORDERS key.
  // -------------------------------------------------------------------------
  async getOrders() {
    return JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.ORDERS) || '[]');
    //                                        key missing → default '[]' → []
  },

  // POST /orders — persist a newly created order
  // Demo: unshift onto the front of the array, write the whole list back.
  async createOrder(orderData) {
    const orders = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.ORDERS) || '[]');
    orders.unshift(orderData); // newest order first
    localStorage.setItem(CONFIG.STORAGE_KEYS.ORDERS, JSON.stringify(orders));
    return orderData; // echo back (mimics API response shape)
  },

  // PATCH /orders/:id/status — update an order's status
  // Demo: find by id, mutate status, write list back. Returns order or undefined.
  async updateOrderStatus(id, status) {
    const orders = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.ORDERS) || '[]');
    const order = orders.find((o) => o.id === id); // locate the order
    if (order) {
      order.status = status; // mutate in place
      localStorage.setItem(CONFIG.STORAGE_KEYS.ORDERS, JSON.stringify(orders)); // save
    }
    return order; // undefined if id not found
  },
};

// Default export → callers do: import API from './api.js'
export default API;