// ============================================================================
// FoodieExpress — auth.js (Demo Authentication)
// ----------------------------------------------------------------------------
// localStorage-based auth for demo purposes ONLY.
// ⚠ Passwords are stored in plaintext — never ship this to production.
//    Replace with real API calls (see api.js) before going live.
// ============================================================================
import { CONFIG, storage } from './config.js';

class Auth {
  constructor() {
    // Load saved session. storage.get() defaults to [] for missing keys,
    // so we re-check for a `token` property to detect a real user object.
    this.user = storage.get(CONFIG.STORAGE_KEYS.USER);
    this.user = this.user && this.user.token ? this.user : null; // object or null
  }

  // True when a session object exists (user is "signed in")
  isAuthenticated() {
    return !!this.user; // !! converts object→true / null→false
  }

  // Returns the current user (or null) — used by profile page to render
  getUser() {
    return this.user;
  }

  // Register a new account, then auto-login with the same credentials.
  async register(name, email, phone, password) {
    await this._delay(600); // simulate network latency (600ms)
    const users = storage.get('fe_users') || []; // all registered demo users

    // Reject duplicate emails (by reference equality on email field)
    if (users.find((u) => u.email === email)) {
      throw new Error('Email already registered');
    }

    // Build the user record (no token yet — issued at login)
    const user = {
      id: `user_${Date.now()}`, // unique-ish id from timestamp
      name, email, phone, password, // ⚠ plaintext password (demo only)
      createdAt: new Date().toISOString(), // ISO-8601 timestamp
    };
    users.push(user);
    storage.set('fe_users', users); // persist the user list
    return this.login(email, password); // immediately sign in
  }

  // Verify credentials and open a demo session
  async login(email, password) {
    await this._delay(600); // simulate network latency
    const users = storage.get('fe_users') || [];
    // Match BOTH email and password (demo-grade check)
    const user = users.find((u) => u.email === email && u.password === password);
    if (!user) {
      throw new Error('Invalid email or password'); // generic message (no leak)
    }
    // Session object = safe subset of user + fake token
    this.user = {
      id: user.id, name: user.name, email: user.email, phone: user.phone,
      token: 'demo_token_' + Date.now(), // fake JWT stand-in
    };
    storage.set(CONFIG.STORAGE_KEYS.USER, this.user); // persist session
    return this.user;
  }

  // Clear session and bounce back to home page
  logout() {
    this.user = null; // drop in-memory session
    storage.remove(CONFIG.STORAGE_KEYS.USER); // drop stored session
    location.href = 'index.html'; // full navigation (resets all state)
  }

  // Promise-based delay to mimic async API calls
  _delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Singleton instance shared by every page that imports this module
export const auth = new Auth();