# FoodieExpress — Frontend

A responsive multi-page food ordering frontend built with HTML5, Bootstrap 5, Bootstrap Icons, and vanilla JavaScript.

## Pages

| Page | Purpose |
|------|---------|
| `index.html` | Restaurant listings and search/filter |
| `menu.html` | Restaurant menu and add-to-cart interactions |
| `cart.html` | Update quantities, remove items, view bill |
| `checkout.html` | Customer details, address, payment selection, order placement |
| `confirmation.html` | Order confirmation with tracking link |
| `delivery.html` | Delivery progress timeline (auto-advances in demo) |
| `orders.html` | Order management dashboard with status updates, cancel, reorder |
| `profile.html` | User account — sign in, sign up, profile details |

## Run it

### Option 1: Open directly
Open `foodieexpress_frontend/index.html` in a browser.

### Option 2: VS Code Live Server
Install the "Live Server" extension in VS Code, right-click `index.html`, and select "Open with Live Server".

### Option 3: Local development server
```bash
cd foodieexpress_frontend
npm install
npm run dev
```

## Architecture

### JavaScript modules (`assets/js/`)

| Module | Responsibility |
|--------|---------------|
| `config.js` | Constants, currency formatting, storage wrapper |
| `data.js` | Restaurant and menu demo data |
| `cart.js` | Cart class — add, remove, change qty, subtotal, total |
| `order.js` | Order manager — create, update status, cancel, reorder, delivery simulation |
| `ui.js` | All DOM rendering and page-specific logic |
| `auth.js` | Demo authentication — register, login, logout |
| `api.js` | API service layer (ready for backend integration) |
| `app.js` | Main entry point — initializes all pages |

### Data flow

1. **Cart**: Stored in `localStorage` key `fe_cart`. Items include restaurantId to prevent mixed-restaurant orders.
2. **Orders**: Stored in `localStorage` key `fe_orders`. Each order has items, customer details, total, payment method, and status.
3. **Active order**: Stored in `localStorage` key `fe_active_order` for delivery tracking.
4. **Auth**: Stored in `localStorage` key `fe_user`. Demo only — passwords are stored in plaintext (not for production).

## Features

- ✅ Restaurant browsing with search and cuisine filter
- ✅ Add to cart, change quantity, remove items
- ✅ Cart prevents mixing items from different restaurants
- ✅ Checkout with delivery details and payment method
- ✅ Demo online payment modal (Razorpay-style)
- ✅ Order confirmation page
- ✅ Delivery status timeline with auto-advancing simulation
- ✅ Order management: view all orders, update status, cancel, reorder
- ✅ User authentication: sign in, sign up, profile management
- ✅ Toast notifications
- ✅ Responsive design (mobile + desktop)

## Testing

### Unit tests (Jest)
```bash
cd foodieexpress_frontend
npm install
npm test
```

### Browser-based test runner
Open `tests/test-runner.html` in a browser for immediate test results without Node.js.

### Test coverage
- `money.test.js` — Currency formatting
- `cart.test.js` — Cart add/remove/qty/subtotal/total/mixed-restaurant prevention
- `order.test.js` — Order create/update/cancel/stats/reorder
- `auth.test.js` — Register/login/logout/duplicate email/invalid credentials

## Deployment

### Netlify (recommended)
1. Push to GitHub
2. Connect your repo to [Netlify](https://netlify.com)
3. Build command: `echo 'No build step required — static site'`
4. Publish directory: `foodieexpress_frontend`
5. Or deploy via CLI: `netlify deploy --dir=foodieexpress_frontend --prod`

### Vercel
1. Push to GitHub
2. Connect your repo to [Vercel](https://vercel.com)
3. Configure with `vercel.json` (already included)
4. Or deploy via CLI: `vercel --prod`

### GitHub Actions CI
A CI workflow (`.github/workflows/ci.yml`) runs on every push and PR:
- Lints JavaScript with ESLint
- Runs Jest unit tests
- Deploys to Netlify on merge to `main`

## Backend Integration

The app is designed to work without a backend (demo mode using `localStorage`). To connect a real backend:

1. Edit `assets/js/api.js` — Replace the mock methods with `fetch()` calls to your API
2. Set `CONFIG.API_BASE_URL` in `assets/js/config.js`
3. Update `assets/js/auth.js` — Replace demo register/login with real API calls
4. Add authentication middleware to protect routes
5. Implement server-side order persistence

## Project structure

```
FoodieExpress/
├── .github/
│   └── workflows/
│       └── ci.yml
├── netlify.toml
├── vercel.json
├── foodieexpress_frontend/
│   ├── README.md
│   ├── package.json
│   ├── jest.config.js
│   ├── babel.config.js
│   ├── index.html
│   ├── menu.html
│   ├── cart.html
│   ├── checkout.html
│   ├── confirmation.html
│   ├── delivery.html
│   ├── orders.html
│   ├── profile.html
│   ├── assets/
│   │   ├── styles.css
│   │   ├── img/
│   │   │   └── food/
│   │   └── js/
│   │       ├── app.js
│   │       ├── config.js
│   │       ├── data.js
│   │       ├── cart.js
│   │       ├── order.js
│   │       ├── ui.js
│   │       ├── auth.js
│   │       └── api.js
│   └── tests/
│       ├── test-runner.html
│       ├── money.test.js
│       ├── cart.test.js
│       ├── order.test.js
│       └── auth.test.js
```

## License

MIT
