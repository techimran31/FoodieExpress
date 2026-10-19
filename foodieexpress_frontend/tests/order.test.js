// FoodieExpress — Order Management Unit Tests
import { orderManager } from '../assets/js/order.js';
import { cart } from '../assets/js/cart.js';

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

document.querySelectorAll = () => [];
window.dispatchEvent = () => true;

describe('OrderManager', () => {
  beforeEach(() => {
    localStorageMock.clear();
    orderManager.orders = [];
    cart.items = [];
  });

  test('starts with no orders', () => {
    expect(orderManager.getAll().length).toBe(0);
  });

  test('creates an order', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    const order = orderManager.create(
      { name: 'John Doe', phone: '9999999999', address: '123 Street, City' },
      'Cash on delivery'
    );
    expect(order.id).toMatch(/^FE\d{6}$/);
    expect(order.status).toBe('Confirmed');
    expect(order.items.length).toBe(1);
    expect(order.total).toBe(249 + 25);
    expect(orderManager.getAll().length).toBe(1);
    expect(cart.isEmpty()).toBe(true);
  });

  test('retrieves order by id', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    const order = orderManager.create(
      { name: 'Jane', phone: '8888888888', address: '456 Ave' },
      'Cash on delivery'
    );
    const found = orderManager.find(order.id);
    expect(found).not.toBeUndefined();
    expect(found.id).toBe(order.id);
  });

  test('updates order status', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    const order = orderManager.create(
      { name: 'Test', phone: '7777777777', address: '789 Rd' },
      'Cash on delivery'
    );
    const result = orderManager.updateStatus(order.id, 'Delivered');
    expect(result).toBe(true);
    expect(orderManager.find(order.id).status).toBe('Delivered');
  });

  test('rejects invalid status', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    const order = orderManager.create(
      { name: 'Test', phone: '7777777777', address: '789 Rd' },
      'Cash on delivery'
    );
    const result = orderManager.updateStatus(order.id, 'Invalid Status');
    expect(result).toBe(false);
  });

  test('cancels order', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    const order = orderManager.create(
      { name: 'Test', phone: '7777777777', address: '789 Rd' },
      'Cash on delivery'
    );
    const result = orderManager.cancel(order.id);
    expect(result).toBe(true);
    expect(orderManager.find(order.id).status).toBe('Cancelled');
  });

  test('calculates stats correctly', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    orderManager.create({ name: 'A', phone: '1', address: '1' }, 'COD');
    cart.add('burger-barn', 'Classic Smash Burger', 229, '🍔');
    const order2 = orderManager.create({ name: 'B', phone: '2', address: '2' }, 'COD');
    orderManager.updateStatus(order2.id, 'Delivered');

    const stats = orderManager.getStats();
    expect(stats.total).toBe(2);
    expect(stats.active).toBe(1);
    expect(stats.revenue).toBe(order2.total);
  });

  test('reorder adds items to cart', () => {
    cart.add('spice-route', 'Chicken Dum Biryani', 249, '🍗');
    const order = orderManager.create(
      { name: 'Test', phone: '1', address: '1' },
      'COD'
    );
    cart.clear();
    expect(cart.isEmpty()).toBe(true);

    const result = orderManager.reorder(order.id);
    expect(result).toBe(true);
    expect(cart.isEmpty()).toBe(false);
    expect(cart.items.length).toBe(1);
    expect(cart.items[0].name).toBe('Chicken Dum Biryani');
  });
});