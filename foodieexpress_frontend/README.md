# FoodieExpress — Frontend Starter

A responsive multi-page food ordering frontend built with HTML5, Bootstrap 5, Bootstrap Icons, and vanilla JavaScript.

## Pages
- `index.html` — restaurant listings and search/filter
- `menu.html` — restaurant menu and add-to-cart interactions
- `cart.html` — update quantities and remove items
- `checkout.html` — customer details, address, payment selection, order placement demo
- `delivery.html` — delivery progress timeline
- `orders.html` — order management dashboard with status updates

## Run it
1. Extract the ZIP.
2. Open `index.html` in a browser, or use VS Code Live Server for the best experience.
3. No backend is connected. Cart and demo orders use `localStorage` in the browser.

## Integration notes
- Replace demo restaurant/menu data in `assets/app.js` with API calls to your backend.
- Connect checkout to a server endpoint before accepting real payments or orders.
- Payment methods are UI-only and do not process payments.
