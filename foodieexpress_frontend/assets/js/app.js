// ============================================================================
// FoodieExpress — app.js (Main Entry Point)
// ----------------------------------------------------------------------------
// Runs once per page AFTER the DOM is fully parsed.
// 1. Wires up global event listeners (cart / order changes).
// 2. Calls every page renderer — each renderer exits early if its target
//    element doesn't exist on the current page (safe to call everywhere).
// 3. Boots engagement widgets (counters, countdown, scroll-reveal, etc.)
// ============================================================================
import { updateCartCount, renderRestaurants, renderMenu, renderCart, renderCheckout, renderDelivery, renderOrders } from './ui.js';

// DOMContentLoaded — fires when HTML is parsed (module scripts are deferred,
// so the DOM is usually ready already; this guard covers both cases).
document.addEventListener('DOMContentLoaded', () => {
  // ---- 1. Sync cart badge in navbar with saved cart ----
  updateCartCount();

  // ---- 2. Render each page's dynamic content (no-ops if element missing) ----
  renderRestaurants();  // index.html  → restaurant grid
  renderMenu();         // menu.html   → menu items list
  renderCart();         // cart.html   → cart line items + totals
  renderCheckout();     // checkout.html → order summary + form wiring
  renderDelivery();     // delivery.html → timeline steps
  renderOrders();       // orders.html → orders table + stats

  // ---- 3. Engagement widgets (defined below) ----
  animateCounters();    // Count-up animation for [data-count]
  startOfferCountdown();// Live timer for #offerCountdown
  observeReveal();      // Reveal-on-scroll for .reveal elements
  initParallaxFloat();  // Gentle parallax for .float-soft hero decorations
});

// ---------------------------------------------------------------------------
// Cart changed → refresh anything that displays cart state on this page.
// Fired by cart.js on add / qty change / remove / clear.
// ---------------------------------------------------------------------------
window.addEventListener('cart:changed', () => {
  updateCartCount();
  renderCart();
  renderCheckout();
});

// ---------------------------------------------------------------------------
// Order updated (status change / cancel / simulation tick) → refresh
// orders table and delivery timeline.
// ---------------------------------------------------------------------------
window.addEventListener('order:updated', () => {
  renderOrders();
  renderDelivery();
});

// ===========================================================================
// ENGAGEMENT HELPERS
// ===========================================================================

// ---------------------------------------------------------------------------
// animateCounters — Count-up effect for stat numbers.
// Finds every [data-count] element, animates 0 → target over 1.2s using
// requestAnimationFrame (smooth 60fps). Optional data-prefix / data-suffix.
// ---------------------------------------------------------------------------
function animateCounters() {
  const els = document.querySelectorAll('[data-count]');
  if (!els.length) return;

  const animate = (el) => {
    const target = Number(el.dataset.count) || 0;   // final number
    const prefix = el.dataset.prefix || '';         // e.g. "₹"
    const suffix = el.dataset.suffix || '';         // e.g. "+"
    const duration = 1200;                          // animation length (ms)
    const start = performance.now();                // timestamp t0

    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1); // clamp 0 → 1
      // Ease-out cubic → fast start, gentle landing
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = prefix + Math.round(target * eased).toLocaleString('en-IN') + suffix;
      if (progress < 1) requestAnimationFrame(tick); // keep animating until done
    };
    requestAnimationFrame(tick); // kick off first frame
  };

  // Only animate when scrolled into view (once)
  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animate(entry.target);
        obs.unobserve(entry.target); // don't re-run on re-entry
      }
    });
  }, { threshold: 0.4 }); // trigger when 40% visible

  els.forEach((el) => io.observe(el));
}

// ---------------------------------------------------------------------------
// startOfferCountdown — Live HH:MM:SS countdown for the offers banner.
// Counts down to midnight (end of daily deal) so the promo always feels
// urgent and "real". Stops displaying once it reaches 00:00:00.
// ---------------------------------------------------------------------------
function startOfferCountdown() {
  const el = document.getElementById('offerCountdown');
  if (!el) return; // page has no countdown widget → exit

  const pad = (n) => String(n).padStart(2, '0'); // 5 → "05"

  const tick = () => {
    const now = new Date();                       // current time
    const end = new Date(now);                    // copy of now…
    end.setHours(24, 0, 0, 0);                    // …moved to next midnight
    let diff = Math.max(0, Math.floor((end - now) / 1000)); // seconds left (floor, ≥0)

    const h = Math.floor(diff / 3600);        // full hours remaining
    const m = Math.floor((diff % 3600) / 60); // minutes after removing hours
    const s = diff % 60;                      // seconds after removing minutes
    el.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`; // e.g. "07:42:15"
  };

  tick();              // paint immediately (no 1s blank wait)
  setInterval(tick, 1000); // then refresh every second
}

// ---------------------------------------------------------------------------
// observeReveal — Adds .revealed to .reveal elements as they scroll in.
// CSS handles the actual transition (opacity/translate); JS only toggles
// the class once per element for performance.
// ---------------------------------------------------------------------------
function observeReveal() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return; // no reveal elements on this page

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed'); // trigger CSS animation
        obs.unobserve(entry.target);            // one-shot — never re-fire
      }
    });
  }, { threshold: 0.15 }); // fire when 15% visible

  els.forEach((el) => io.observe(el));
}

// ---------------------------------------------------------------------------
// initParallaxFloat — Mouse-move parallax for hero decorations.
// Elements marked .float-soft move a few pixels opposite to the cursor for
// subtle depth. Disabled on touch devices (hover:none → no mousemove).
// ---------------------------------------------------------------------------
function initParallaxFloat() {
  const hero = document.getElementById('hero');       // hero section (index only)
  const floats = document.querySelectorAll('.float-soft'); // movable decorations
  if (!hero || !floats.length) return;                // not on this page
  if (window.matchMedia('(hover: none)').matches) return;  // skip touch devices

  hero.addEventListener('mousemove', (e) => {
    const rect = hero.getBoundingClientRect();        // hero's on-screen box
    // Normalize cursor to -0.5 … +0.5 around the hero center
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    floats.forEach((el) => {
      const depth = Number(el.dataset.depth) || 20;   // parallax strength (px)
      el.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
    });
  });
}