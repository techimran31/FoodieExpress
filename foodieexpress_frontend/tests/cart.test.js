// FoodieExpress — Cart Unit Tests
import { money } from '../assets/js/config.js';
import { Cart } from '../assets/js/cart.js';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value; },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock document.querySelectorAll for cart count updates
document.querySelectorAll = () => [];

describe('money()', () => {
  test('formats zero correctly', () => {
    expect(money(0)).toBe('₹0');
  });

  test('formats whole numbers', () => {
    expect(money(249)).toBe('₹249');
  });

  test('formats with thousands separator', () => {
    expect(money(1250)).toBe('₹1,250');
  });

  test('formats decimals', () => {
    expect(money(249.50)).toBe('₹249.50');
  });
});

describe('Cart', () => {
  let cart;

  beforeEach(() => {
    localStorageMock.clear();
    cart = new Cart();
  });

  test('starts empty', () => {
    expect(cart.isEmpty()).toBe(true);
    expect(cart.getItemCount()).toBe(0);
    expect(cart.getSubtotal()).toBe(0);
    expect(cart.getTotal()).toBe(0);
  });

  test('add item to cart', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    expect(cart.isEmpty()).toBe(false);
    expect(cart.getItemCount()).toBe(1);
    expect(cart.items[0].name).toBe('Chicken Dum Biryani');
    expect(cart.items[0].qty).toBe(1);
    expect(cart.items[0].price).toBe(249);
  });

  test('increases quantity of existing item', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    expect(cart.getItemCount()).toBe(2);
    expect(cart.items[0].qty).toBe(2);
  });

  test('changes quantity', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.changeQty(0, 2);
    expect(cart.items[0].qty).toBe(3);
  });

  test('removes item when qty goes to zero', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.changeQty(0, -1);
    expect(cart.isEmpty()).toBe(true);
  });

  test('removes item by index', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.add('spice-route', 'Butter Naan', 45, '🫓');
    cart.removeItem(0);
    expect(cart.items.length).toBe(1);
    expect(cart.items[0].name).toBe('Butter Naan');
  });

  test('calculates subtotal correctly', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.add('spice-route', 'Butter Naan', 45, '🫓');
    cart.changeQty(0, 1); // 2 biryanis
    expect(cart.getSubtotal()).toBe(249 * 2 + 45);
  });

  test('calculates delivery fee', () => {
    expect(cart.getDeliveryFee()).toBe(0); // empty cart
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    expect(cart.getDeliveryFee()).toBe(25);
  });

  test('calculates total correctly', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    expect(cart.getTotal()).toBe(249 + 25);
  });

  test('clears cart', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.clear();
    expect(cart.isEmpty()).toBe(true);
  });

  test('prevents mixed restaurants in cart', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    cart.add('burger-barn', 'Classic Smash Burger', 229, '🍔');
    // Should only keep items from the first restaurant
    expect(cart.items.length).toBe(1);
    expect(cart.items[0].restaurantId).toBe('spice-route');
  });
});