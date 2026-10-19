// FoodieExpress — Cart Logic
import { CONFIG, storage, money } from './config.js';

class Cart {
  constructor() {
    this.items = storage.get(CONFIG.STORAGE_KEYS.CART);
    this._validateCart();
  }

  _validateCart() {
    // Remove items from different restaurants if cart has mixed restaurants
    // Keep only items from the first restaurant found
    if (this.items.length > 1) {
      const firstRestaurantId = this.items[0].restaurantId;
      this.items = this.items.filter((item) => item.restaurantId === firstRestaurantId);
      this.save();
    }
  }

  save() {
    storage.set(CONFIG.STORAGE_KEYS.CART, this.items);
    this.updateCartCount();
  }

  updateCartCount() {
    const totalQty = this.items.reduce((sum, item) => sum + item.qty, 0);
    document.querySelectorAll('[data-cart-count]').forEach((el) => {
      el.textContent = totalQty;
    });
  }

  add(restaurantId, itemName, price, emoji) {
    const restaurantName = window.restaurants
      ? window.restaurants.find((r) => r.id === restaurantId)?.name || 'Restaurant'
      : 'Restaurant';

    // If cart has items from a different restaurant, clear and start fresh
    if (this.items.length > 0 && this.items[0].restaurantId !== restaurantId) {
      this.items = [];
    }

    const existing = this.items.find((i) => i.restaurantId === restaurantId && i.name === itemName);
    if (existing) {
      existing.qty += 1;
    } else {
      this.items.push({
        restaurantId,
        restaurant: restaurantName,
        name: itemName,
        price: Number(price),
        emoji,
        qty: 1,
      });
    }
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: this.items } }));
    return this.items;
  }

  changeQty(index, delta) {
    if (!this.items[index]) return;
    this.items[index].qty += delta;
    if (this.items[index].qty <= 0) {
      this.items.splice(index, 1);
    }
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: this.items } }));
    return this.items;
  }

  removeItem(index) {
    if (!this.items[index]) return;
    this.items.splice(index, 1);
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: this.items } }));
    return this.items;
  }

  clear() {
    this.items = [];
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: [] } }));
  }

  getSubtotal() {
    return this.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  }

  getDeliveryFee() {
    return this.items.length > 0 ? CONFIG.DELIVERY_FEE : 0;
  }

  getTotal() {
    return this.getSubtotal() + this.getDeliveryFee();
  }

  getItemCount() {
    return this.items.reduce((sum, item) => sum + item.qty, 0);
  }

  isEmpty() {
    return this.items.length === 0;
  }
}

export const cart = new Cart();