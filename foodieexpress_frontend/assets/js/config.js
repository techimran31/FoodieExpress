// ============================================================================
// FoodieExpress — config.js
// ----------------------------------------------------------------------------
// Central configuration & shared helpers.
// Every other module imports from here so constants live in ONE place.
// ============================================================================

// Application-wide settings object (frozen conceptually — treat as read-only)
export const CONFIG = {
  APP_NAME: 'FoodieExpress',        // Brand name used in titles/toasts
  CURRENCY: '₹',                    // Indian Rupee symbol (display only)
  CURRENCY_LOCALE: 'en-IN',         // Locale used by toLocaleString (1,00,000 format)
  DELIVERY_FEE: 25,                 // Flat delivery fee charged when cart is not empty
  // localStorage keys — prefixed "fe_" to avoid collisions with other sites
  STORAGE_KEYS: {
    CART: 'fe_cart',                // Stores the cart items array
    ORDERS: 'fe_orders',            // Stores all placed orders array
    ACTIVE_ORDER: 'fe_active_order',// Stores the id of the order shown on delivery page
    USER: 'fe_user',                // Stores the currently signed-in demo user
  },
  // Valid order statuses — index order = delivery pipeline order
  ORDER_STATUSES: ['Confirmed', 'Preparing', 'Picked up', 'Out for delivery', 'Delivered', 'Cancelled'],
  // Future: base URL for a real backend API (empty = demo/local mode)
  API_BASE_URL: '',
};

// ---------------------------------------------------------------------------
// money(n) — Formats a number as Indian currency string, e.g. 1299 → "₹1,299"
//   1. Number(n)        → ensures we work with a real number (not string)
//   2. toLocaleString() → applies en-IN grouping rules (lakh/crore commas)
//   3. Template literal  → prepends the ₹ symbol
// ---------------------------------------------------------------------------
export const money = (n) => `${CONFIG.CURRENCY}${Number(n).toLocaleString(CONFIG.CURRENCY_LOCALE)}`;

// ---------------------------------------------------------------------------
// storage — Tiny wrapper around localStorage with JSON safe-parsing.
// Prevents repeated try/catch boilerplate and JSON errors across the app.
// ---------------------------------------------------------------------------
export const storage = {
  // Read a key → parse JSON. Falls back to [] if missing/corrupt.
  get(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || '[]'); // '[]' default keeps arrays safe
    } catch {
      return []; // Corrupted data → return empty array instead of crashing
    }
  },
  // Write a value → stringify + store under the key
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  },
  // Delete a key entirely (used on logout)
  remove(key) {
    localStorage.removeItem(key);
  },
};