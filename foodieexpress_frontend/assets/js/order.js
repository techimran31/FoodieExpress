// ============================================================================
// FoodieExpress — order.js (Order Lifecycle Management)
// ----------------------------------------------------------------------------
// Handles: creating orders, status transitions, cancellation, statistics,
// reorder, and a DEMO auto-delivery simulation (timers advance the status
// Confirmed → Preparing → Picked up → Out for delivery → Delivered).
// ============================================================================
import { CONFIG, storage } from './config.js';
import { cart } from './cart.js';

class OrderManager {
  constructor() {
    this.orders = storage.get(CONFIG.STORAGE_KEYS.ORDERS); // saved orders[]
    this._simulationTimers = new Map(); // orderId → setInterval handle
  }

  // Persist orders[] to localStorage
  save() {
    storage.set(CONFIG.STORAGE_KEYS.ORDERS, this.orders);
  }

  // All orders, NEWEST first (copy via spread so caller can't mutate original)
  getAll() {
    return [...this.orders].reverse();
  }

  // Find one order by its id (e.g. "FE482913") — undefined if not found
  find(id) {
    return this.orders.find((o) => o.id === id);
  }

  // -------------------------------------------------------------------------
  // create(customer, paymentMethod) — Convert the current cart into an order.
  //   • Throws if cart is empty (can't order nothing)
  //   • Generates a random 6-digit order id with "FE" prefix
  //   • Clears cart + stores as active order + starts delivery simulation
  // -------------------------------------------------------------------------
  create(customer, paymentMethod) {
    if (cart.isEmpty()) {
      throw new Error('Cannot place order with empty cart'); // caught by ui.js
    }

    const order = {
      id: `FE${Math.floor(100000 + Math.random() * 900000)}`, // FE123456
      date: new Date().toISOString(),  // ISO timestamp for sorting/display
      status: 'Confirmed',             // first status in the pipeline
      items: [...cart.items],          // snapshot (spread → cart can change freely)
      total: cart.getTotal(),          // subtotal + delivery fee
      customer,                        // { name, phone, address }
      payment: paymentMethod,          // "Cash on delivery" | "Online payment (demo)"
    };

    this.orders.unshift(order);        // newest order at index 0
    this.save();                       // persist to localStorage
    storage.set(CONFIG.STORAGE_KEYS.ACTIVE_ORDER, order.id); // delivery.html target
    cart.clear();                      // basket is now empty
    this.startDeliverySimulation(order.id); // begin demo status auto-advance
    return order;                      // caller redirects to confirmation page
  }

  // -------------------------------------------------------------------------
  // updateStatus(id, status) — Manual or simulated status change.
  // Validates: order exists AND status is in CONFIG.ORDER_STATUSES.
  // Broadcasts 'order:updated' so orders/delivery pages re-render.
  // -------------------------------------------------------------------------
  updateStatus(id, status) {
    const order = this.find(id);
    if (!order) return false;                              // unknown id
    if (!CONFIG.ORDER_STATUSES.includes(status)) return false; // invalid status
    order.status = status;
    this.save();
    window.dispatchEvent(new CustomEvent('order:updated', { detail: { order } }));
    return true;
  }

  // Cancel = stop simulation + set status to "Cancelled"
  cancel(id) {
    const order = this.find(id);
    if (!order) return false;
    this._stopSimulation(id);                 // halt auto-advance timers
    return this.updateStatus(id, 'Cancelled'); // reuse validated update path
  }

  // Id of the order delivery.html should display (saved choice, else newest)
  getActiveId() {
    return storage.get(CONFIG.STORAGE_KEYS.ACTIVE_ORDER) || (this.orders[0]?.id || null);
    // storage.get returns [] for missing key → falls through via || to newest
  }

  // Save which order the user chose to track
  setActiveId(id) {
    storage.set(CONFIG.STORAGE_KEYS.ACTIVE_ORDER, id);
  }

  // -------------------------------------------------------------------------
  // getStats() — Aggregates for the orders.html dashboard header:
  //   total   → every order ever placed
  //   active  → not Delivered AND not Cancelled
  //   revenue → sum of totals excluding cancelled orders
  // -------------------------------------------------------------------------
  getStats() {
    const all = this.orders;
    return {
      total: all.length,
      active: all.filter((o) => o.status !== 'Delivered' && o.status !== 'Cancelled').length,
      revenue: all
        .filter((o) => o.status !== 'Cancelled') // cancelled orders don't count
        .reduce((sum, o) => sum + o.total, 0),
    };
  }

  // ---- Delivery simulation (demo only) ----

  // ==========================================================================
  // DEMO DELIVERY SIMULATION
  // A setInterval "advances" the order through the pipeline every 90 seconds
  // to demonstrate live tracking without a real backend.
  // ==========================================================================

  // Start (or restart) the auto-advance timer for one order
  startDeliverySimulation(orderId) {
    this._stopSimulation(orderId); // idempotent — kill any existing timer first
    const order = this.find(orderId);
    // Nothing to simulate if order is missing or already terminal
    if (!order || order.status === 'Delivered' || order.status === 'Cancelled') return;

    const statuses = CONFIG.ORDER_STATUSES.slice(0, 5); // Confirmed..Delivered (drop Cancelled)
    const currentIdx = statuses.indexOf(order.status);   // where we are now
    // Already at/past "Delivered"? → nothing left to animate
    if (currentIdx < 0 || currentIdx >= statuses.length - 1) return;

    const delays = [90, 90, 90, 90]; // seconds between each status change
    let idx = currentIdx;            // cursor walking through statuses[]

    // Schedule the NEXT status tick (delay derived from current position)
    const timer = setInterval(() => {
      idx += 1;                                  // advance one step
      if (idx >= statuses.length) {              // safety: ran past the end
        this._stopSimulation(orderId);
        return;
      }
      this.updateStatus(orderId, statuses[idx]); // persist + broadcast event
      if (statuses[idx] === 'Delivered' || statuses[idx] === 'Cancelled') {
        this._stopSimulation(orderId);           // terminal state → stop timer
      }
    }, delays[idx - 1] * 1000); // delays[old idx] → seconds → milliseconds

    this._simulationTimers.set(orderId, timer); // remember handle for cleanup
  }

  // Clear ONE order's interval timer (if it exists) and forget the handle
  _stopSimulation(orderId) {
    const timer = this._simulationTimers.get(orderId);
    if (timer) {
      clearInterval(timer);                 // stop ticking
      this._simulationTimers.delete(orderId); // free the map entry
    }
  }

  // Halt ALL timers (used when leaving the app or resetting demo state)
  stopAllSimulations() {
    this._simulationTimers.forEach((timer) => clearTimeout(timer)); // cancel each
    this._simulationTimers.clear(); // empty the map
  }

  // ==========================================================================
  // REORDER — Copy a past order's items back into the cart (then checkout)
  // ==========================================================================
  reorder(orderId) {
    const order = this.find(orderId);
    if (!order || !order.items || !order.items.length) return false; // nothing to copy

    cart.items = []; // start from an empty basket (bypasses single-rest check)
    order.items.forEach((item) => {
      cart.items.push({ // re-create each line exactly as it was ordered
        restaurantId: item.restaurantId,
        restaurant: item.restaurant,
        name: item.name,
        price: item.price,
        emoji: item.emoji,
        qty: item.qty,
      });
    });
    cart.save(); // persist + refresh badges
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: cart.items } }));
    return true; // caller shows success toast + redirects to cart
  }
}

// Singleton instance shared by ui.js (renders) and inline HTML handlers
export const orderManager = new OrderManager();