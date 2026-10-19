// FoodieExpress — Main Entry Point
import { updateCartCount, renderRestaurants, renderMenu, renderCart, renderCheckout, renderDelivery, renderOrders } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
  updateCartCount();
  renderRestaurants();
  renderMenu();
  renderCart();
  renderCheckout();
  renderDelivery();
  renderOrders();
});

// Listen for cart changes across pages (e.g., when navigating back)
window.addEventListener('cart:changed', () => {
  updateCartCount();
  renderCart();
  renderCheckout();
});

// Listen for order updates
window.addEventListener('order:updated', () => {
  renderOrders();
  renderDelivery();
});