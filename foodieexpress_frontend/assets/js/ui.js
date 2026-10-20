// ============================================================================
// FoodieExpress — ui.js (UI Rendering & DOM Manipulation)
// ----------------------------------------------------------------------------
// The "V" in this vanilla-JS app:
//   • Builds HTML strings for each page section
//   • Injects them into containers by element id
//   • Exposes window.* globals used by inline onclick handlers
// Each render function exits early when its container doesn't exist, so
// every page can safely import and call ALL renderers.
// ============================================================================
import { CONFIG, money } from './config.js';   // config + currency formatter
import { restaurants, findRestaurant, getMenu } from './data.js'; // demo data
import { cart } from './cart.js';             // cart singleton
import { orderManager } from './order.js';    // order singleton

// Expose data globally for inline HTML event handlers & api.js (backward compat)
window.restaurants = restaurants;

// Expose toast() as window.showToast → used by inline onclick handlers
// (e.g. the newsletter "Join free" button on index.html)
window.showToast = toast;

// ---------------------------------------------------------------------------
// toast(msg, celebrate=false) — Transient bottom-right notification.
//   1. Lazily creates a fixed .toast-container on first call
//   2. Injects a Bootstrap-style toast with ✓ (normal) or 🎉 (celebration)
//   3. Auto-clears after 2.5s
// ---------------------------------------------------------------------------
export function toast(msg, celebrate = false) {
  let el = document.getElementById('toast');
  if (!el) { // first toast on this page → build the container
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    el.style.zIndex = '1055'; // above navbar (1030) + modals (1060 area)
    document.body.appendChild(el);
  }
  // Inner toast markup (show = visible immediately, no toggle needed)
  el.innerHTML = `
    <div class="toast show border-0 shadow-lg rounded-4" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-body d-flex align-items-center gap-2 p-3">
        <span class="text-success fw-bold fs-4">${celebrate ? '🎉' : '✓'}</span>
        <div class="fw-semibold">${msg}</div>
      </div>
    </div>`;
  setTimeout(() => { el.innerHTML = ''; }, 2500); // hide after 2.5 seconds
}

// ---------------------------------------------------------------------------
// celebrate() — Confetti burst overlay.
// Creates a full-screen, pointer-transparent layer, spawns 60 colored pieces
// that fall with random duration/shape, then removes the layer entirely.
// ---------------------------------------------------------------------------
export function celebrate() {
  const colors = ['#ff6b00', '#ffeaa7', '#00b894', '#74b9ff', '#fd79a8']; // brand palette
  const confettiCount = 60; // number of pieces
  const container = document.createElement('div'); // overlay layer
  container.style.position = 'fixed';  // cover viewport…
  container.style.top = '0';
  container.style.left = '0';
  container.style.width = '100%';
  container.style.height = '100%';
  container.style.pointerEvents = 'none'; // never block clicks
  container.style.zIndex = '9999';        // above everything
  document.body.appendChild(container);

  for (let i = 0; i < confettiCount; i++) { // spawn each confetti piece
    const piece = document.createElement('div');
    piece.style.position = 'absolute';
    piece.style.width = '8px';           // small square…
    piece.style.height = '8px';
    piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)]; // random color
    piece.style.left = Math.random() * 100 + 'vw'; // random horizontal start
    piece.style.top = '-10px';           // start just above viewport
    piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '0'; // circle or square
    piece.style.animation = `confettiFall ${Math.random() * 1 + 1}s linear forwards`; // 1–2s fall
    container.appendChild(piece);
  }

  setTimeout(() => container.remove(), 2000); // clean up when animation ends
}

// ---- Cart Count ----
// Thin wrapper → delegates to cart singleton (keeps import list stable)
export function updateCartCount() {
  cart.updateCartCount();
}

// ---------------------------------------------------------------------------
// renderRestaurants() — index.html restaurant grid.
//   1. Injects one card per restaurant
//   2. Binds LIVE search + cuisine-filter (input/change events)
//   3. Toggles #noRestaurants empty-state when zero matches remain
// Guard: exits immediately on pages without #restaurantGrid.
// ---------------------------------------------------------------------------
export function renderRestaurants() {
  const grid = document.getElementById('restaurantGrid');
  if (!grid) return; // not index.html → nothing to render

  grid.innerHTML = restaurants.map(restaurantCard).join(''); // array → HTML string

  const search = document.getElementById('restaurantSearch'); // text input
  const filter = document.getElementById('cuisineFilter');    // <select>
  if (!search || !filter) return; // controls missing → cards still show

  // apply() — Recompute visibility of every card against current query+filter
  function apply() {
    const q = search.value.toLowerCase();   // lowercase query ("biryani")
    const f = filter.value;                 // selected cuisine or "" (all)
    let count = 0;                          // visible cards (for empty-state)
    document.querySelectorAll('.restaurant-card').forEach((el) => {
      // Card matches if its data-search haystack contains BOTH q and the filter
      const show = el.dataset.search.includes(q) && (!f || el.dataset.search.includes(f.toLowerCase()));
      el.classList.toggle('d-none', !show); // Bootstrap utility: show/hide
      if (show) count += 1;
    });
    const noMatch = document.getElementById('noRestaurants');
    if (noMatch) noMatch.classList.toggle('d-none', count > 0); // hide banner if any match
  }

  // Re-bind listeners: remove first so re-renders never double-fire
  search.removeEventListener('input', apply);
  filter.removeEventListener('change', apply);
  search.addEventListener('input', apply);   // type → instant filtering
  filter.addEventListener('change', apply);  // pick → instant filtering
}

// ---------------------------------------------------------------------------
// restaurantCard(r) — HTML template for ONE restaurant card.
// Engagement touches added in the redesign:
//   • Offer ribbon pinned on the image (visual hook)
//   • Wishlist heart (top-right) toggles a saved state
//   • Green rating chip + hover lift handled purely by CSS (.food-card)
// data-search = name + cuisine + tags → powers the live filter above.
// ---------------------------------------------------------------------------
function restaurantCard(r) {
  const searchStr = `${r.name} ${r.cuisine} ${r.tags.join(' ')}`.toLowerCase();
  return `
    <div class="col-sm-6 col-lg-4 restaurant-card" data-search="${searchStr}">
      <article class="food-card h-100 position-relative">
        <a href="menu.html?restaurant=${r.id}" class="text-dark text-decoration-none d-block">
          <div class="food-emoji" style="background:${r.color}">${r.emoji}</div>
        </a>
        <!-- Promotional ribbon over the image -->
        <span class="offer-ribbon">${r.offer}</span>
        <!-- Wishlist heart — window.toggleWishlist persists to localStorage -->
        <button class="wishlist-btn ${getWishlist().includes(r.id) ? 'saved' : ''}" type="button" aria-label="Save ${r.name}"
                onclick="event.preventDefault(); window.toggleWishlist('${r.id}', this)">
          <i class="${getWishlist().includes(r.id) ? 'bi bi-heart-fill' : 'bi bi-heart'}"></i>
        </button>
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
            <span class="text-brand small fw-bold"><i class="bi bi-lightning-charge-fill me-1"></i>${r.offer}</span>
            <a class="btn btn-sm btn-outline-brand" href="menu.html?restaurant=${r.id}">
              View menu <i class="bi bi-arrow-right ms-1"></i>
            </a>
          </div>
        </div>
      </article>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// renderMenu() — menu.html dynamic content.
//   1. Reads ?restaurant=<id> from the URL (falls back to 'spice-route')
//   2. Fills hero (name/cuisine/rating/time) + builds the dish list
//   3. Each "Add" button calls window.addToCart(...) inline
//   4. Refreshes the sticky order sidebar + checkout CTA state
// ---------------------------------------------------------------------------
export function renderMenu() {
  const params = new URLSearchParams(location.search); // parse query string
  const id = params.get('restaurant') || 'spice-route'; // selected restaurant id
  const r = findRestaurant(id);  // restaurant object (safe fallback inside)
  const list = getMenu(id);      // array of [name, desc, price, emoji, badge]

  // Update every placeholder tagged with data-restaurant-name / -cuisine
  document.querySelectorAll('[data-restaurant-name]').forEach((e) => { e.textContent = r.name; });
  document.querySelectorAll('[data-restaurant-cuisine]').forEach((e) => { e.textContent = r.cuisine; });

  // --- Hero section: emoji tile + rating + delivery time ---
  const hero = document.getElementById('menuHero');
  if (hero) {
    const emojiEl = hero.querySelector('.menu-hero-emoji');
    if (emojiEl) {
      emojiEl.textContent = r.emoji;      // big food emoji
      emojiEl.style.background = r.color; // pastel tile behind it
    }
    const ratingEl = hero.querySelector('[data-rating]');
    if (ratingEl) ratingEl.textContent = `★ ${r.rating}`; // star + number
    const timeEl = hero.querySelector('[data-time]');
    if (timeEl) timeEl.textContent = r.time;               // "25–35 min"
  }

  const container = document.getElementById('menuItems');
  if (!container) return; // not menu.html → stop here

  // Build dish rows; animate-in delay staggers entrance (0s, 0.1s, 0.2s…)
  container.innerHTML = list.map((m, i) => `
    <div class="menu-item animate-in" style="animation-delay: ${i * 0.1}s">
      <div class="menu-emoji">${m[3]}</div>
      <div class="menu-info">
        <div class="d-flex gap-2 flex-wrap mb-1">
          <span class="pill">${m[4]}</span>
        </div>
        <h3 class="h6 fw-bold mb-1">${m[0]}</h3>
        <p class="small muted mb-2">${m[1]}</p>
        <span class="price">${money(m[2])}</span>
      </div>
      <button class="btn btn-brand btn-sm px-4 py-2" onclick="window.addToCart('${r.id}', ${JSON.stringify(m[0])}, ${m[2]}, '${m[3]}')">
        Add <i class="bi bi-plus-lg ms-2"></i>
      </button>
    </div>
  `).join('');
  //        JSON.stringify(m[0]) → safely quotes dish names with apostrophes

  renderMenuSidebar(); // refresh sticky cart summary
  updateCheckoutButton(); // enable/disable "Checkout" CTA
}

// ---------------------------------------------------------------------------
// renderMenuSidebar() — Right-hand sticky summary on menu.html.
// Shows item count badge, line items (with trash), subtotal/fee/total.
// Empty cart → friendly 🛒 empty-state message.
// ---------------------------------------------------------------------------
export function renderMenuSidebar() {
  const items = cart.items; // current basket lines
  const badge = document.getElementById('cartItemBadge');   // "N items"
  const sidebar = document.getElementById('sidebarItems');  // line list
  const subEl = document.getElementById('sidebarSubtotal'); // ₹ subtotal
  const delEl = document.getElementById('sidebarDelivery'); // ₹ fee
  const totalEl = document.getElementById('sidebarTotal');  // ₹ total

  if (badge) badge.textContent = `${items.length} items`;
  if (subEl) subEl.textContent = money(cart.getSubtotal());
  if (delEl) delEl.textContent = money(cart.getDeliveryFee());
  if (totalEl) totalEl.textContent = money(cart.getTotal());

  if (!sidebar) return; // no sidebar container → done
  if (!items.length) {  // EMPTY STATE → cheerful placeholder
    sidebar.innerHTML = `
      <div class="text-center py-4">
        <div class="fs-2 mb-3">🛒</div>
        <p class="small muted mb-0">Your cart is empty</p>
      </div>`;
    return;
  }
  // Render each line: emoji tile, name, qty×price, delete button
  sidebar.innerHTML = items.map((item, index) => `
    <div class="d-flex gap-3 mb-3 p-3 rounded-4" style="background:#f8f9fa;border:1px solid var(--fx-border)">
      <div class="menu-emoji" style="width:48px;height:48px;font-size:1.8rem">${item.emoji}</div>
      <div class="flex-grow-1 d-flex flex-column justify-content-between">
        <div class="fw-bold">${item.name}</div>
        <div class="small muted">${item.qty} × ${money(item.price)}</div>
      </div>
      <button class="btn btn-sm text-danger p-0" onclick="window.removeItem(${index})" title="Remove">
        <i class="bi bi-trash"></i>
      </button>
    </div>
  `).join('');
}

// ---------------------------------------------------------------------------
// updateCheckoutButton() — Grey out #checkoutBtn while cart is empty.
// When items exist → re-enable + attach a ONE-SHOT click → checkout.html.
// ({ once: true } guarantees no duplicate handlers after re-renders.)
// ---------------------------------------------------------------------------
export function updateCheckoutButton() {
  const btn = document.getElementById('checkoutBtn');
  if (!btn) return; // page has no checkout CTA
  if (cart.isEmpty()) {
    btn.disabled = true;           // block navigation…
    btn.classList.add('disabled'); // …and grey styling
    btn.style.opacity = '0.5';
  } else {
    btn.disabled = false;
    btn.classList.remove('disabled');
    btn.style.opacity = '1';
    btn.addEventListener('click', () => {
      location.href = 'checkout.html'; // navigate to checkout
    }, { once: true }); // auto-removes after first click
  }
}

// ---------------------------------------------------------------------------
// renderCart() — cart.html line items + totals.
// Empty basket → show #emptyCart block, hide #cartContent (and vice versa).
// Each line: big emoji, name, restaurant, line total, trash + qty stepper.
// Qty buttons call window.changeQty(index, ±1) → cart re-renders instantly.
// ---------------------------------------------------------------------------
export function renderCart() {
  const list = document.getElementById('cartItems'); // line-items container
  if (!list) return; // not cart.html → exit

  const items = cart.items;
  const empty = document.getElementById('emptyCart');   // 🗑 empty CTA block
  const content = document.getElementById('cartContent');// items + bill block

  // Toggle visibility based on whether the basket has lines
  if (empty) empty.classList.toggle('d-none', items.length > 0);
  if (content) content.classList.toggle('d-none', items.length === 0);
  if (!items.length) return; // nothing to draw

  // Draw each cart line (border-top only on rows after the first)
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

  // --- Bill summary (subtotal / delivery / total) ---
  const sub = cart.getSubtotal();
  const subEl = document.getElementById('cartSubtotal');
  const delEl = document.getElementById('cartDelivery');
  const totalEl = document.getElementById('cartTotal');
  if (subEl) subEl.textContent = money(sub);
  if (delEl) delEl.textContent = money(cart.getDeliveryFee());
  if (totalEl) totalEl.textContent = money(cart.getTotal());
}

// ---------------------------------------------------------------------------
// renderCheckout() — checkout.html order summary + form submission logic.
// Flow:
//   • EMPTY basket → hide form/aside, show #checkoutEmpty CTA
//   • FILLED  → fill item rows + totals, then (re)bind the form
//   • Form submit → validate → "Cash on delivery" places order directly;
//     "Online payment" opens the demo #paymentModal first.
// NOTE: form is CLONED (cloneNode) to strip stale listeners on re-render.
// ---------------------------------------------------------------------------
export function renderCheckout() {
  const items = cart.items;
  const box = document.getElementById('checkoutItemsList'); // summary rows
  const aside = document.getElementById('checkoutAside');   // bill card
  if (!box) return; // not checkout.html → exit

  // --- EMPTY STATE: hide everything order-related, show the empty CTA ---
  if (!items.length) {
    const formWrap = document.getElementById('checkoutFormWrap');
    const emptyEl = document.getElementById('checkoutEmpty');
    if (formWrap) formWrap.classList.add('d-none');
    if (aside) aside.classList.add('d-none');
    if (emptyEl) emptyEl.classList.remove('d-none');
    return;
  }

  if (aside) aside.classList.remove('d-none'); // basket has items → show bill

  // One summary line per cart entry: "2 × Burger … ₹458"
  box.innerHTML = items.map((i) => `
    <div class="summary-row">
      <span>${i.qty} × ${i.name}</span>
      <span>${money(i.qty * i.price)}</span>
    </div>
  `).join('');

  // --- Totals + make sure form is visible ---
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
    // Clone+replace = guaranteed-fresh listeners (avoids duplicate submits)
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);

    const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
    const demoPayBtn = document.getElementById('demoPayBtn'); // "Pay now" button
    const modalAmount = document.getElementById('modalAmount'); // amount echo
    let pendingOrderData = null; // order waiting for successful payment

    // Keep modal amount in sync whenever the cart changes
    const updateModalAmount = () => {
      if (modalAmount) modalAmount.textContent = money(cart.getTotal());
    };
    updateModalAmount(); // paint once on load
    window.addEventListener('cart:changed', updateModalAmount); // live updates

    // "Pay (demo)" clicked → pretend payment succeeded → place the order
    demoPayBtn.addEventListener('click', () => {
      modal.hide(); // close the payment modal
      if (pendingOrderData) {
        try {
          const order = orderManager.create(pendingOrderData.customer, pendingOrderData.payment);
          toast('Payment successful! Order placed.');
          location.href = 'confirmation.html'; // success page (shows confetti)
        } catch (err) {
          toast(err.message || 'Failed to place order. Please try again.');
        }
        pendingOrderData = null; // clear the pending payload
      }
    });

    // Form submitted → read fields → decide direct vs modal payment path
    newForm.addEventListener('submit', (e) => {
      e.preventDefault(); // stop native GET submit (page reload)
      if (!newForm.reportValidity()) return; // HTML5 validation gate

      const customer = {
        name: newForm.customerName.value.trim(),
        phone: newForm.phone.value.trim(),
        address: newForm.address.value.trim(),
      };
      const payment = newForm.payment.value; // radio: COD / Online (demo)

      // Online path → stash data + open payment modal
      if (payment === 'Online payment (demo)') {
        pendingOrderData = { customer, payment };
        updateModalAmount();
        modal.show();
        return;
      }

      // Cash path → place order immediately
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

// ---------------------------------------------------------------------------
// renderDelivery() — delivery.html tracking panel.
//   • Picks the ACTIVE order (user's choice stored, else newest)
//   • Fills customer/address/total/items summary cards
//   • Walks the 5-step timeline: marks each [data-step] .done / .active
//   • Shows colored status badge (Delivered=green, Cancelled=red)
// ---------------------------------------------------------------------------
export function renderDelivery() {
  const orders = orderManager.getAll();        // newest-first list
  const activeId = orderManager.getActiveId(); // chosen order id (or newest)
  const order = orderManager.find(activeId) || orders[0]; // fallback chain

  const wrap = document.getElementById('deliveryContent');
  if (!wrap) return; // not delivery.html → exit

  // --- NO ORDERS YET → friendly empty state with CTA ---
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

  // --- Summary cards (each guarded so partial pages don't crash) ---
  const orderIdEl = document.getElementById('deliveryOrderId');
  const customerEl = document.getElementById('deliveryCustomer');
  const addressEl = document.getElementById('deliveryAddress');
  const totalEl = document.getElementById('deliveryTotal');
  const itemsEl = document.getElementById('deliveryItems');
  const statusEl = document.getElementById('deliveryStatus');

  if (orderIdEl) orderIdEl.textContent = `#${order.id}`; // "#FE482913"
  if (customerEl) customerEl.textContent = order.customer?.name || 'Customer';
  if (addressEl) addressEl.textContent = order.customer?.address || 'Address not provided';
  if (totalEl) totalEl.textContent = money(order.total);
  if (itemsEl) itemsEl.textContent = order.items.map((i) => `${i.qty} × ${i.name}`).join(', ');

  // --- Timeline: map status string → step index (0=Confirmed … 4=Delivered) ---
  const statuses = CONFIG.ORDER_STATUSES.slice(0, 5); // drop "Cancelled"
  let current = statuses.indexOf(order.status);
  if (current < 0) current = 0; // Cancelled/unknown → highlight first step

  document.querySelectorAll('[data-step]').forEach((el) => {
    const n = Number(el.dataset.step); // this step's position
    el.classList.toggle('done', n < current);   // finished steps → checkmark
    el.classList.toggle('active', n === current); // current step → pulse
  });

  // --- Status badge (class drives the color) ---
  if (statusEl) {
    statusEl.textContent = order.status;
    statusEl.className = `status-badge ${order.status === 'Delivered' ? 'status-delivered' : order.status === 'Cancelled' ? 'status-cancelled' : ''}`;
  }
}

// ---------------------------------------------------------------------------
// renderOrders() — orders.html history table + dashboard stats.
//   • Stats header: total / active / revenue (from orderManager.getStats())
//   • Empty basket of orders → show #emptyOrders, hide #ordersTableWrap
//   • Each row: id+date, customer, items, total, STATUS <select>,
//     Track / Cancel / Reorder action buttons (inline onclick handlers)
// ---------------------------------------------------------------------------
export function renderOrders() {
  const table = document.getElementById('ordersTableBody');
  if (!table) return; // not orders.html → exit

  const orders = orderManager.getAll(); // newest first
  const stats = orderManager.getStats(); // { total, active, revenue }

  const countEl = document.getElementById('orderCount');    // stat: all orders
  const activeEl = document.getElementById('activeCount');  // stat: in-progress
  const revenueEl = document.getElementById('revenueCount');// stat: ₹ earned
  const emptyEl = document.getElementById('emptyOrders');   // empty-state block
  const wrapEl = document.getElementById('ordersTableWrap');// table wrapper

  if (countEl) countEl.textContent = stats.total;
  if (activeEl) activeEl.textContent = stats.active;
  if (revenueEl) revenueEl.textContent = money(stats.revenue);
  if (emptyEl) emptyEl.classList.toggle('d-none', orders.length > 0); // hide if orders exist
  if (wrapEl) wrapEl.classList.toggle('d-none', orders.length === 0); // hide table if none

  // Build one <tr> per order
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
        <!-- Status editor: changing select pushes update via window.updateOrderStatus -->
        <select class="form-select form-select-sm" style="min-width:145px"
                onchange="window.updateOrderStatus('${o.id}', this.value)">
          ${CONFIG.ORDER_STATUSES.map((s) => `<option ${o.status === s ? 'selected' : ''}>${s}</option>`).join('')}
        </select>
      </td>
      <td>
        <a href="delivery.html" class="btn btn-sm btn-light" onclick="window.setActiveOrder('${o.id}')">Track</a>
        ${['Confirmed', 'Preparing', 'Picked up', 'Out for delivery'].includes(o.status)
          ? `<button class="btn btn-sm btn-outline-danger ms-1" onclick="window.cancelOrder('${o.id}')">Cancel</button>`
          : '' /* only in-progress orders can be cancelled */
        }
        ${o.status === 'Delivered'
          ? `<button class="btn btn-sm btn-outline-brand ms-1" onclick="window.reorderOrder('${o.id}')">Reorder</button>`
          : '' /* only completed orders can be reordered */
        }
      </td>
    </tr>
  `).join('');
}

// ===========================================================================
// GLOBAL FUNCTIONS — called directly from inline HTML onclick/onchange attrs.
// Module scope is NOT global, so each handler is deliberately hung on window.
// ===========================================================================

// Add a dish to the cart + confirm with a toast
window.addToCart = (restaurantId, itemName, price, emoji) => {
  cart.add(restaurantId, itemName, price, emoji); // mutate + persist + broadcast
  toast(`${itemName} added to your cart`);        // instant feedback
};

// Qty stepper: adjust one line, then re-draw cart + checkout panels
window.changeQty = (index, delta) => {
  cart.changeQty(index, delta); // handles qty≤0 → line removal
  renderCart();
  renderCheckout();
};

// Trash icon: delete a line outright
window.removeItem = (index) => {
  cart.removeItem(index);
  renderCart();
  renderCheckout();
};

// Orders table status <select> → validate + persist + refresh both views
window.updateOrderStatus = (id, status) => {
  orderManager.updateStatus(id, status);
  renderOrders();
  renderDelivery();
  toast('Order status updated');
};

// Cancel button → browser confirm → halt simulation → mark Cancelled
window.cancelOrder = (id) => {
  if (!confirm('Are you sure you want to cancel this order?')) return; // abort on "Cancel"
  orderManager.cancel(id);
  renderOrders();
  renderDelivery();
  toast('Order cancelled');
};

// "Track" link → remember which order delivery.html should display
window.setActiveOrder = (id) => {
  orderManager.setActiveId(id);
};

// "Reorder" → clone past items into cart → toast → jump to cart page
window.reorderOrder = (id) => {
  if (orderManager.reorder(id)) {
    toast('Items added to cart! Proceed to checkout.');
    location.href = 'cart.html';
  } else {
    toast('Unable to reorder this order.'); // order had no items
  }
};

// ---------------------------------------------------------------------------
// Wishlist helpers — saved restaurant ids in localStorage ("fe_wishlist").
// getWishlist()     → id[] (safe default [])
// toggleWishlist()  → flip saved state, restyle the heart, toast the result
// ---------------------------------------------------------------------------
function getWishlist() {
  try {
    return JSON.parse(localStorage.getItem('fe_wishlist') || '[]'); // parse saved ids
  } catch {
    return []; // corrupted → treat as empty
  }
}

window.toggleWishlist = (id, btn) => {
  let list = getWishlist();
  const saved = list.includes(id); // already liked?
  if (saved) {
    list = list.filter((x) => x !== id); // unlike → remove id
  } else {
    list.push(id); // like → append id
  }
  localStorage.setItem('fe_wishlist', JSON.stringify(list)); // persist
  if (btn) { // restyle this heart instantly (no full re-render needed)
    btn.classList.toggle('saved', !saved);
    const icon = btn.querySelector('i');
    if (icon) icon.className = saved ? 'bi bi-heart' : 'bi bi-heart-fill'; // outline ↔ filled
  }
  toast(saved ? 'Removed from your favourites' : 'Added to your favourites ❤️');
};