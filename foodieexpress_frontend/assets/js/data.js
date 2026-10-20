// ============================================================================
// FoodieExpress — data.js (Demo Data: Restaurants & Menus)
// ----------------------------------------------------------------------------
// Static seed data used in demo mode (no backend).
// Swap these arrays for API responses when a backend exists.
// ============================================================================

// ---------------------------------------------------------------------------
// RESTAURANTS — each object powers one card on index.html
//   id        → URL slug used in menu.html?restaurant=<id>
//   name      → display name
//   cuisine   → subtitle shown under the name
//   rating    → star rating (shown in .rating badge)
//   time      → delivery estimate string
//   fee       → delivery fee in ₹ (used by card pill)
//   offer     → promo line (e.g. "20% off")
//   emoji     → big card image substitute (food emoji)
//   color     → pastel background behind the emoji
//   tags      → cuisine keywords for search/filter matching
// ---------------------------------------------------------------------------
export const restaurants = [
  { id: 'spice-route', name: 'Spice Route Kitchen', cuisine: 'Indian · Biryani', rating: 4.7, time: '25–35 min', fee: 25, offer: '20% off', emoji: '🍛', color: '#ffe2c7', tags: ['Indian', 'Biryani'] },
  { id: 'burger-barn', name: 'Burger Barn', cuisine: 'Burgers · Fast Food', rating: 4.5, time: '20–30 min', fee: 20, offer: 'Free fries', emoji: '🍔', color: '#ffe8a8', tags: ['Burgers', 'Fast Food'] },
  { id: 'green-bowl', name: 'Green Bowl Co.', cuisine: 'Healthy · Salads', rating: 4.6, time: '20–30 min', fee: 15, offer: 'Healthy picks', emoji: '🥗', color: '#dff3d9', tags: ['Healthy', 'Salads'] },
  { id: 'pizza-works', name: 'Pizza Works', cuisine: 'Pizza · Italian', rating: 4.4, time: '30–40 min', fee: 30, offer: 'Buy 1 get 1', emoji: '🍕', color: '#ffd8ce', tags: ['Pizza', 'Italian'] },
  { id: 'noodle-house', name: 'Noodle House', cuisine: 'Asian · Noodles', rating: 4.6, time: '25–35 min', fee: 20, offer: '15% off', emoji: '🍜', color: '#ffe0a8', tags: ['Asian', 'Noodles'] },
  { id: 'sweet-cloud', name: 'Sweet Cloud', cuisine: 'Desserts · Bakery', rating: 4.8, time: '15–25 min', fee: 10, offer: 'Sweet treats', emoji: '🧁', color: '#f7dff0', tags: ['Desserts', 'Bakery'] },
];

// ---------------------------------------------------------------------------
// MENUS — keyed by restaurant id.
// Each item is a tuple: [name, description, price, emoji, badge]
//   price → number in ₹ (no symbol — money() adds it)
//   badge → short tag like "Bestseller" / "Veg" (shown as a pill)
// ---------------------------------------------------------------------------
export const menus = {
  'spice-route': [
    ['Chicken Dum Biryani', 'Fragrant basmati rice, tender chicken and house spices.', 249, '🍗', 'Bestseller'],
    ['Paneer Butter Masala', 'Paneer in a rich tomato and butter gravy.', 219, '🧀', 'Veg'],
    ['Veg Biryani', 'Seasonal vegetables, herbs and aromatic rice.', 179, '🍚', 'Veg'],
    ['Butter Naan', 'Soft tandoor-baked naan brushed with butter.', 45, '🫓', 'Popular'],
  ],
  'burger-barn': [
    ['Classic Smash Burger', 'Double-seared patty, cheddar, pickles and house sauce.', 229, '🍔', 'Bestseller'],
    ['Crispy Veg Burger', 'Crunchy vegetable patty with fresh lettuce.', 159, '🥬', 'Veg'],
    ['Loaded Fries', 'Golden fries with cheese sauce and herbs.', 129, '🍟', 'Popular'],
    ['Chocolate Shake', 'Thick chocolate milkshake.', 119, '🥤', 'Drinks'],
  ],
  'green-bowl': [
    ['Rainbow Power Bowl', 'Quinoa, greens, roasted vegetables and tahini.', 249, '🥗', 'Healthy'],
    ['Paneer Protein Bowl', 'Grilled paneer, brown rice and crunchy greens.', 229, '🧀', 'Veg'],
    ['Avocado Toast', 'Sourdough toast, avocado and lemon.', 189, '🥑', 'Popular'],
  ],
  'pizza-works': [
    ['Margherita Pizza', 'Classic tomato, mozzarella and basil.', 249, '🍕', 'Veg'],
    ['Farmhouse Pizza', 'Peppers, onion, mushrooms and olives.', 329, '🍕', 'Bestseller'],
    ['Garlic Bread', 'Toasted bread with garlic butter.', 119, '🥖', 'Popular'],
  ],
  'noodle-house': [
    ['Chilli Garlic Noodles', 'Wok-tossed noodles with garlic and vegetables.', 189, '🍜', 'Popular'],
    ['Chicken Hakka Noodles', 'Noodles, chicken and crisp vegetables.', 229, '🍜', 'Bestseller'],
    ['Veg Spring Rolls', 'Crispy rolls with a savoury vegetable filling.', 139, '🥢', 'Veg'],
  ],
  'sweet-cloud': [
    ['Chocolate Lava Cake', 'Warm chocolate cake with a molten centre.', 149, '🍰', 'Bestseller'],
    ['Red Velvet Cupcake', 'Soft red velvet sponge with cream cheese frosting.', 99, '🧁', 'Popular'],
    ['Classic Cheesecake', 'Creamy baked cheesecake slice.', 179, '🍰', 'Dessert'],
  ],
};

// ---------------------------------------------------------------------------
// Helper lookups (fail-safe with fallbacks so pages never crash)
// findRestaurant(id) → restaurant object, or first restaurant if id unknown
// getMenu(id)        → menu array, or Spice Route's menu if id unknown
// ---------------------------------------------------------------------------
export const findRestaurant = (id) => restaurants.find((r) => r.id === id) || restaurants[0];
export const getMenu = (restaurantId) => menus[restaurantId] || menus['spice-route'];