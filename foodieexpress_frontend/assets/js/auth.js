// FoodieExpress — Authentication (demo, localStorage-based)
import { CONFIG, storage } from './config.js';

class Auth {
  constructor() {
    this.user = storage.get(CONFIG.STORAGE_KEYS.USER);
    this.user = this.user && this.user.token ? this.user : null;
  }

  isAuthenticated() {
    return !!this.user;
  }

  getUser() {
    return this.user;
  }

  async register(name, email, phone, password) {
    // Demo: simulate API call
    await this._delay(600);
    const users = storage.get('fe_users') || [];
    if (users.find((u) => u.email === email)) {
      throw new Error('Email already registered');
    }
    const user = { id: `user_${Date.now()}`, name, email, phone, password, createdAt: new Date().toISOString() };
    users.push(user);
    storage.set('fe_users', users);
    return this.login(email, password);
  }

  async login(email, password) {
    await this._delay(600);
    const users = storage.get('fe_users') || [];
    const user = users.find((u) => u.email === email && u.password === password);
    if (!user) {
      throw new Error('Invalid email or password');
    }
    this.user = { id: user.id, name: user.name, email: user.email, phone: user.phone, token: 'demo_token_' + Date.now() };
    storage.set(CONFIG.STORAGE_KEYS.USER, this.user);
    return this.user;
  }

  logout() {
    this.user = null;
    storage.remove(CONFIG.STORAGE_KEYS.USER);
    location.href = 'index.html';
  }

  _delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export const auth = new Auth();