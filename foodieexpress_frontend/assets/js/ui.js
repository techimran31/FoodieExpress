// FoodieExpress — UI Rendering & DOM Manipulation
import { CONFIG, money } from './config.js';
import { restaurants, findRestaurant, getMenu } from './data.js';
import { cart } from './cart.js';
import { orderManager } from './order.js';

// Expose data globally for inline HTML event handlers (backward compat)
window.restaurants = restaurants;

// Toast notification
export function toast(msg) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    el.style.zIndex = '1055';
    document.body.appendChild(el);
  }
  el.innerHTML = `
    <div class="toast show border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-body d-flex align-items-center gap-2">
        <span class="text-success">✓</span>${msg}
      </div>
    </div>`;
  setTimeout(() => { el.innerHTML = ''; }, 2200);
}

// ---- Cart Count ----
export function updateCartCount() {
  cart.updateCartCount();
}

// ---- Restaurants (index.html) ----
export function renderRestaurants() {
  const grid = document.getElementById('restaurantGrid');
  if (!grid) return;

  grid.innerHTML = restaurants.map(restaurantCard).join('');

  const search = document.getElementById('restaurantSearch');
  const filter = document.getElementById('cuisineFilter');
  if (!search || !filter) return;

  function apply() {
    const q = search.value.toLowerCase();
    const f = filter.value;
    let count = 0;
    document.querySelectorAll('.restaurant-card').forEach((el) => {
      const show = el.dataset.search.includes(q) && (!f || el.dataset.search.includes(f.toLowerCase()));
      el.classList.toggle('d-none', !show);
      if (show) count += 1;
    });
    const noMatch = document.getElementById('noRestaurants');
    if (noMatch) noMatch.classList.toggle('d-none', count > 0);
  }

  search.removeEventListener('input', apply);
  filter.removeEventListener('change', apply);
  search.addEventListener('input', apply);
  filter.addEventListener('change', apply);
}

function restaurantCard(r) {
  const searchStr = `${r.name} ${r.cuisine} ${r.tags.join(' ')}`.toLowerCase();
  return `
    <div class="col-sm-6 col-lg-4 restaurant-card" data-search="${searchStr}">
      <article class="food-card h-100">
        <a href="menu.html?restaurant=${r.id}" class="text-dark text-decoration-none">
          <div class="food-emoji" style="background:${r.color}">${r.emoji}</div>
        </a>
        <div class="card-body">
          <div class="d-flex justify-content-between gap-2 align-items-start">
            <h3 class="h5 fw-bold mb-1">${r.name}</h3>
            <span class="rating">★ ${r.rating}</span>
          </div>
          <p class="muted small mb-3">${r.cuisine}</p>
          <div class="d-flex flex-wrap gap-2 align-items-center">
            <span class="pill"><i class="bi bi-clock me-1"></i>${r.time}</span>
            <span class="pill">${money(r.fee)} delivery</span>
          </div>
          <div class="mt-3 d-flex justify-content-between align-items-center">
            <span class="text-brand small fw-bold">${r.offer}</span>
            <a class="btn btn-sm btn-outline-brand" href="menu.html?restaurant=${r.id}">
              View menu <i class="bi bi-arrow-right ms-1"></i>
            </a>
          </div>
        </div>
      </article>
    </div>
  `;
}

// ---- Menu (menu.html) ----
export function renderMenu() {
  const params = new URLSearchParams(location.search);
  const id = params.get('restaurant') || 'spice-route';
  const r = findRestaurant(id);
  const list = getMenu(id);

  document.querySelectorAll('[data-restaurant-name]').forEach((e) => { e.textContent = r.name; });
  document.querySelectorAll('[data-restaurant-cuisine]').forEach((e) => { e.textContent = r.cuisine; });

  const hero = document.getElementById('menuHero');
  if (hero) {
    const emojiEl = hero.querySelector('.menu-hero-emoji');
    if (emojiEl) {
      emojiEl.textContent = r.emoji;
      emojiEl.style.background = r.color;
    }
    const ratingEl = hero.querySelector('[data-rating]');
    if (ratingEl) ratingEl.textContent = `★ ${r.rating}`;
    const timeEl = hero.querySelector('[data-time]');
    if (timeEl) timeEl.textContent = r.time;
  }

  const container = document.getElementById('menuItems');
  if (!container) return;

  container.innerHTML = list.map((m, i) => `
    <div class="menu-item mb-3">
      <div class="menu-emoji">${m[3]}</div>
      <div class="menu-info">
        <div class="d-flex gap-2 flex-wrap mb-1">
          <span class="pill">${m[4]}</span>
        </div>
        <h3 class="h6 fw-bold mb-1">${m[0]}</h3>
        <p class="small muted mb-2">${m[1]}</p>
        <span class="price">${money(m[2])}</span>
      </div>
      <button class="btn btn-outline-brand btn-sm px-3" onclick="window.addToCart('${r.id}', ${JSON.stringify(m[0])}, ${m[2]}, '${m[3]}')">
        Add <i class="bi bi-plus-lg ms-1"></i>
      </button>
    </div>
  `).join('');

  const link = document.getElementById('viewCartLink');
  if (link) link.href = 'cart.html';
}

// ---- Cart (cart.html) ----
export function renderCart() {
  const list = document.getElementById('cartItems');
  if (!list) return;

  const items = cart.items;
  const empty = document.getElementById('emptyCart');
  const content = document.getElementById('cartContent');

  if (empty) empty.classList.toggle('d-none', items.length > 0);
  if (content) content.classList.toggle('d-none', items.length === 0);
  if (!items.length) return;

  list.innerHTML = items.map((item, index) => `
    <div class="d-flex gap-3 py-3 ${index ? 'border-top' : ''}">
      <div class="menu-emoji" style="width:68px;height:68px;font-size:2rem">${item.emoji}</div>
      <div class="flex-grow-1">
        <div class="fw-bold">${item.name}</div>
        <div class="small muted">${item.restaurant}</div>
        <div class="price mt-1">${money(item.price * item.qty)}</div>
      </div>
      <div class="d-flex flex-column align-items-end justify-content-between">
        <button class="btn btn-sm text-secondary p-0" aria-label="Remove item" onclick="window.removeItem(${index})">
          <i class="bi bi-trash"></i>
        </button>
        <div class="d-flex align-items-center gap-2">
          <button class="btn btn-light qty-btn" onclick="window.changeQty(${index}, -1)">−</button>
          <span class="fw-bold">${item.qty}</span>
          <button class="btn btn-light qty-btn" onclick="window.changeQty(${index}, 1)">+</button>
        </div>
      </div>
    </div>
  `).join('');

  const sub = cart.getSubtotal();
  const subEl = document.getElementById('cartSubtotal');
  const delEl = document.getElementById('cartDelivery');
  const totalEl = document.getElementById('cartTotal');
  if (subEl) subEl.textContent = money(sub);
  if (delEl) delEl.textContent = money(cart.getDeliveryFee());
  if (totalEl) totalEl.textContent = money(cart.getTotal());
}

// ---- Checkout (checkout.html) ----
export function renderCheckout() {
  const items = cart.items;
  const box = document.getElementById('checkoutItemsList');
  const aside = document.getElementById('checkoutAside');
  if (!box) return;

  if (!items.length) {
    const formWrap = document.getElementById('checkoutFormWrap');
    const emptyEl = document.getElementById('checkoutEmpty');
    if (formWrap) formWrap.classList.add('d-none');
    if (aside) aside.classList.add('d-none');
    if (emptyEl) emptyEl.classList.remove('d-none');
    return;
  }

  if (aside) aside.classList.remove('d-none');

  box.innerHTML = items.map((i) => `
    <div class="summary-row">
      <span>${i.qty} × ${i.name}</span>
      <span>${money(i.qty * i.price)}</span>
    </div>
  `).join('');

  const subEl = document.getElementById('checkoutSubtotal');
  const feeEl = document.getElementById('checkoutFee');
  const totalEl = document.getElementById('checkoutTotal');
  const emptyEl = document.getElementById('checkoutEmpty');
  const formWrap = document.getElementById('checkoutFormWrap');
  if (subEl) subEl.textContent = money(cart.getSubtotal());
  if (feeEl) feeEl.textContent = money(cart.getDeliveryFee());
  if (totalEl) totalEl.textContent = money(cart.getTotal());
  if (emptyEl) emptyEl.classList.add('d-none');
  if (formWrap) formWrap.classList.remove('d-none');

  const form = document.getElementById('checkoutForm');
  if (form) {
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);

    const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
    const demoPayBtn = document.getElementById('demoPayBtn');
    const modalAmount = document.getElementById('modalAmount');
    let pendingOrderData = null;

    // Update modal amount whenever totals change
    const updateModalAmount = () => {
      if (modalAmount) modalAmount.textContent = money(cart.getTotal());
    };
    updateModalAmount();
    window.addEventListener('cart:changed', updateModalAmount);

    demoPayBtn.addEventListener('click', () => {
      modal.hide();
      if (pendingOrderData) {
        try {
          const order = orderManager.create(pendingOrderData.customer, pendingOrderData.payment);
          toast('Payment successful! Order placed.');
          location.href = 'confirmation.html';
        } catch (err) {
          toast(err.message || 'Failed to place order. Please try again.');
        }
        pendingOrderData = null;
      }
    });

    newForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!newForm.reportValidity()) return;

      const customer = {
        name: newForm.customerName.value.trim(),
        phone: newForm.phone.value.trim(),
        address: newForm.address.value.trim(),
      };
      const payment = newForm.payment.value;

      if (payment === 'Online payment (demo)') {
        pendingOrderData = { customer, payment };
        updateModalAmount();
        modal.show();
        return;
      }

      try {
        const order = orderManager.create(customer, payment);
        toast('Order placed successfully!');
        location.href = 'confirmation.html';
      } catch (err) {
        toast(err.message || 'Failed to place order. Please try again.');
      }
    });
  }
}

// ---- Delivery (delivery.html) ----
export function renderDelivery() {
  const orders = orderManager.getAll();
  const activeId = orderManager.getActiveId();
  const order = orderManager.find(activeId) || orders[0];

  const wrap = document.getElementById('deliveryContent');
  if (!wrap) return;

  if (!order) {
    wrap.innerHTML = `
      <div class="empty-state">
        <div class="display-4 mb-3">🛵</div>
        <h2 class="h4 fw-bold">No active delivery yet</h2>
        <p class="muted">Place an order to follow its progress here.</p>
        <a href="index.html" class="btn btn-brand">Browse restaurants</a>
      </div>`;
    return;
  }

  const orderIdEl = document.getElementById('deliveryOrderId');
  const customerEl = document.getElementById('deliveryCustomer');
  const addressEl = document.getElementById('deliveryAddress');
  const totalEl = document.getElementById('deliveryTotal');
  const itemsEl = document.getElementById('deliveryItems');
  const statusEl = document.getElementById('deliveryStatus');

  if (orderIdEl) orderIdEl.textContent = `#${order.id}`;
  if (customerEl) customerEl.textContent = order.customer?.name || 'Customer';
  if (addressEl) addressEl.textContent = order.customer?.address || 'Address not provided';
  if (totalEl) totalEl.textContent = money(order.total);
  if (itemsEl) itemsEl.textContent = order.items.map((i) => `${i.qty} × ${i.name}`).join(', ');

  const statuses = CONFIG.ORDER_STATUSES.slice(0, 5);
  let current = statuses.indexOf(order.status);
  if (current < 0) current = 0;

  document.querySelectorAll('[data-step]').forEach((el) => {
    const n = Number(el.dataset.step);
    el.classList.toggle('done', n < current);
    el.classList.toggle('active', n === current);
  });

  if (statusEl) {
    statusEl.textContent = order.status;
    statusEl.className = `status-badge ${order.status === 'Delivered' ? 'status-delivered' : order.status === 'Cancelled' ? 'status-cancelled' : ''}`;
  }
}

// ---- Orders (orders.html) ----
export function renderOrders() {
  const table = document.getElementById('ordersTableBody');
  if (!table) return;

  const orders = orderManager.getAll();
  const stats = orderManager.getStats();

  const countEl = document.getElementById('orderCount');
  const activeEl = document.getElementById('activeCount');
  const revenueEl = document.getElementById('revenueCount');
  const emptyEl = document.getElementById('emptyOrders');
  const wrapEl = document.getElementById('ordersTableWrap');

  if (countEl) countEl.textContent = stats.total;
  if (activeEl) activeEl.textContent = stats.active;
  if (revenueEl) revenueEl.textContent = money(stats.revenue);
  if (emptyEl) emptyEl.classList.toggle('d-none', orders.length > 0);
  if (wrapEl) wrapEl.classList.toggle('d-none', orders.length === 0);

  table.innerHTML = orders.map((o) => `
    <tr>
      <td>
        <span class="fw-bold">#${o.id}</span>
        <div class="small muted">${new Date(o.date).toLocaleDateString()}</div>
      </td>
      <td>
        ${o.customer?.name || 'Customer'}
        <div class="small muted">${o.customer?.phone || ''}</div>
      </td>
      <td>
        ${o.items.reduce((s, i) => s + i.qty, 0)} items
        <div class="small muted text-truncate" style="max-width:220px">${o.items.map((i) => i.name).join(', ')}</div>
      </td>
      <td class="fw-bold">${money(o.total)}</td>
      <td>
        <select class="form-select form-select-sm" style="min-width:145px"
                onchange="window.updateOrderStatus('${o.id}', this.value)">
          ${CONFIG.ORDER_STATUSES.map((s) => `<option ${o.status === s ? 'selected' : ''}>${s}</option>`).join('')}
        </select>
      </td>
      <td>
        <a href="delivery.html" class="btn btn-sm btn-light" onclick="window.setActiveOrder('${o.id}')">Track</a>
        ${['Confirmed', 'Preparing', 'Picked up', 'Out for delivery'].includes(o.status)
          ? `<button class="btn btn-sm btn-outline-danger ms-1" onclick="window.cancelOrder('${o.id}')">Cancel</button>`
          : ''
        }
        ${o.status === 'Delivered'
          ? `<button class="btn btn-sm btn-outline-brand ms-1" onclick="window.reorderOrder('${o.id}')">Reorder</button>`
          : ''
        }
      </td>
    </tr>
  `).join('');
}

// ---- Global functions for inline HTML handlers ----
window.addToCart = (restaurantId, itemName, price, emoji) => {
  cart.add(restaurantId, itemName, price, emoji);
  toast(`${itemName} added to your cart`);
};

window.changeQty = (index, delta) => {
  cart.changeQty(index, delta);
  renderCart();
  renderCheckout();
};

window.removeItem = (index) => {
  cart.removeItem(index);
  renderCart();
  renderCheckout();
};

window.updateOrderStatus = (id, status) => {
  orderManager.updateStatus(id, status);
  renderOrders();
  renderDelivery();
  toast('Order status updated');
};

window.cancelOrder = (id) => {
  if (!confirm('Are you sure you want to cancel this order?')) return;
  orderManager.cancel(id);
  renderOrders();
  renderDelivery();
  toast('Order cancelled');
};

window.setActiveOrder = (id) => {
  orderManager.setActiveId(id);
};

window.reorderOrder = (id) => {
  if (orderManager.reorder(id)) {
    toast('Items added to cart! Proceed to checkout.');
    location.href = 'cart.html';
  } else {
    toast('Unable to reorder this order.');
  }
};