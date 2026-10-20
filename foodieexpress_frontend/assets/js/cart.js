// ============================================================================
// FoodieExpress — cart.js (Shopping Cart Logic)
// ----------------------------------------------------------------------------
// The Cart class is the single source of truth for the user's basket.
// - Persists to localStorage (survives page reloads)
// - Enforces "one restaurant at a time" (mixing restaurants is blocked)
// - Broadcasts a 'cart:changed' CustomEvent after EVERY mutation so any
//   page can re-render its cart-dependent UI.
// ============================================================================
import { CONFIG, storage, money } from './config.js';

class Cart {
  // Runs once when the module loads (singleton pattern below)
  constructor() {
    this.items = storage.get(CONFIG.STORAGE_KEYS.CART); // load saved items
    this._validateCart(); // clean up mixed-restaurant leftovers
  }

  // -------------------------------------------------------------------------
  // _validateCart — Safety net on load.
  // If an old/corrupt cart holds items from MULTIPLE restaurants, keep only
  // the first restaurant's items and save the cleaned result.
  // -------------------------------------------------------------------------
  _validateCart() {
    if (this.items.length > 1) {
      const firstRestaurantId = this.items[0].restaurantId; // restaurant to keep
      this.items = this.items.filter((item) => item.restaurantId === firstRestaurantId);
      this.save(); // persist the cleaned list
    }
  }

  // save — Write items to localStorage + refresh every cart badge on page.
  save() {
    storage.set(CONFIG.STORAGE_KEYS.CART, this.items);
    this.updateCartCount();
  }

  // updateCartCount — Update ALL elements carrying [data-cart-count]
  // (navbar badge, hero button, offcanvas menu, etc.) with total quantity.
  updateCartCount() {
    const totalQty = this.items.reduce((sum, item) => sum + item.qty, 0); // Σ qty
    document.querySelectorAll('[data-cart-count]').forEach((el) => {
      el.textContent = totalQty;
    });
  }

  // -------------------------------------------------------------------------
  // add(restaurantId, name, price, emoji) — Add one unit of a menu item.
  //   1. Resolve restaurant name (via window.restaurants, fallback "Restaurant")
  //   2. Cart holds a DIFFERENT restaurant? → clear first (single-rest rule)
  //   3. Item already in cart → qty++ ; else push new line with qty 1
  //   4. Save + broadcast 'cart:changed'
  // -------------------------------------------------------------------------
  add(restaurantId, itemName, price, emoji) {
    const restaurantName = window.restaurants
      ? window.restaurants.find((r) => r.id === restaurantId)?.name || 'Restaurant'
      : 'Restaurant'; // fallback if data not loaded

    // Single-restaurant rule: swap restaurants → empty the basket
    if (this.items.length > 0 && this.items[0].restaurantId !== restaurantId) {
      this.items = [];
    }

    // Find an existing line for the SAME restaurant + SAME dish
    const existing = this.items.find((i) => i.restaurantId === restaurantId && i.name === itemName);
    if (existing) {
      existing.qty += 1; // increment quantity on existing line
    } else {
      this.items.push({   // create a brand-new line item
        restaurantId,
        restaurant: restaurantName,
        name: itemName,
        price: Number(price), // coerce string prices to number
        emoji,
        qty: 1,
      });
    }
    this.save(); // persist + update badges
    // Notify listeners (ui.js re-renders cart/checkout panels)
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: this.items } }));
    return this.items;
  }

  // -------------------------------------------------------------------------
  // changeQty(index, delta) — +/- one unit on line `index`.
  // delta = +1 → increase, -1 → decrease.
  // If quantity drops to 0 → the line is removed entirely.
  // -------------------------------------------------------------------------
  changeQty(index, delta) {
    if (!this.items[index]) return; // guard: index out of range
    this.items[index].qty += delta;
    if (this.items[index].qty <= 0) {
      this.items.splice(index, 1); // remove line (qty hit zero)
    }
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: this.items } }));
    return this.items;
  }

  // -------------------------------------------------------------------------
  // removeItem(index) — Delete a line regardless of quantity.
  // -------------------------------------------------------------------------
  removeItem(index) {
    if (!this.items[index]) return; // guard: index out of range
    this.items.splice(index, 1);    // cut the line
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: this.items } }));
    return this.items;
  }

  // clear() — Empty the whole cart (called after an order is placed).
  clear() {
    this.items = [];
    this.save();
    window.dispatchEvent(new CustomEvent('cart:changed', { detail: { items: [] } }));
  }

  // ---- Money helpers (used by cart / checkout / menu sidebars) ----

  // Subtotal = Σ (price × qty) for all lines
  getSubtotal() {
    return this.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  }

  // Delivery fee: flat ₹25 when cart has items, else free (0)
  getDeliveryFee() {
    return this.items.length > 0 ? CONFIG.DELIVERY_FEE : 0;
  }

  // Grand total = subtotal + delivery fee
  getTotal() {
    return this.getSubtotal() + this.getDeliveryFee();
  }

  // Total UNITS (e.g. 2× fries + 1× burger = 3)
  getItemCount() {
    return this.items.reduce((sum, item) => sum + item.qty, 0);
  }

  // True when basket has no lines (drives empty-state UI)
  isEmpty() {
    return this.items.length === 0;
  }
}

// Singleton instance — every import of this module shares ONE cart object
export const cart = new Cart();