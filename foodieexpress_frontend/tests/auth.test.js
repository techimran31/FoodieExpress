// FoodieExpress — Authentication Unit Tests
import { auth } from '../assets/js/auth.js';

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

describe('Auth', () => {
  beforeEach(() => {
    localStorageMock.clear();
    auth.user = null;
    localStorageMock.setItem('fe_users', '[]');
  });

  test('starts unauthenticated', () => {
    expect(auth.isAuthenticated()).toBe(false);
    expect(auth.getUser()).toBeNull();
  });

  test('registers and logs in a user', async () => {
    await auth.register('Test User', 'test@example.com', '9999999999', 'password123');
    expect(auth.isAuthenticated()).toBe(true);
    const user = auth.getUser();
    expect(user.name).toBe('Test User');
    expect(user.email).toBe('test@example.com');
    expect(user.token).toBeDefined();
  });

  test('rejects duplicate email', async () => {
    await auth.register('Test User', 'test@example.com', '9999999999', 'password123');
    await expect(auth.register('Test 2', 'test@example.com', '8888888888', 'password123')).rejects.toThrow('Email already registered');
  });

  test('rejects invalid credentials', async () => {
    await auth.register('Test User', 'test@example.com', '9999999999', 'password123');
    await expect(auth.login('test@example.com', 'wrongpassword')).rejects.toThrow('Invalid email or password');
    await expect(auth.login('nonexistent@example.com', 'password123')).rejects.toThrow('Invalid email or password');
  });

  test('logs out user', async () => {
    await auth.register('Test User', 'test@example.com', '9999999999', 'password123');
    expect(auth.isAuthenticated()).toBe(true);
    auth.logout();
    expect(auth.isAuthenticated()).toBe(false);
    expect(auth.getUser()).toBeNull();
  });
});