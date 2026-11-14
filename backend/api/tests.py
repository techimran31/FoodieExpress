from django.test import Client, TestCase

from .models import Dish, DineoutVenue, Order, Restaurant


class PageTests(TestCase):
    def test_pages_render(self):
        client = Client()
        for page in [
            "/", "/index.html", "/restaurants.html", "/restaurant.html",
            "/dineout.html", "/cart.html", "/checkout.html", "/payments.html",
            "/orders.html", "/track.html", "/auth.html", "/account.html",
            "/help.html", "/partner.html",
        ]:
            with self.subTest(page=page):
                self.assertEqual(client.get(page).status_code, 200)

    def test_assets_and_clean_urls(self):
        client = Client()
        self.assertEqual(client.get("/assets/css/app.css").status_code, 200)
        self.assertEqual(client.get("/assets/img/logo.png").status_code, 200)
        res = client.get("/restaurants?cuisine=Pizza")
        self.assertEqual(res.status_code, 302)
        self.assertIn("restaurants.html", res["Location"])


class RestaurantApiTests(TestCase):
    def test_seeded_data_and_filters(self):
        self.assertGreater(Restaurant.objects.count(), 10)
        self.assertGreater(Dish.objects.count(), 90)

        client = Client()
        data = client.get("/api/restaurants").json()
        self.assertGreaterEqual(data["count"], 10)

        pizza = client.get("/api/restaurants?cuisine=Pizza").json()
        self.assertGreaterEqual(pizza["count"], 1)

        nonveg = client.get("/api/restaurants?nonveg=true").json()
        veg = client.get("/api/restaurants?veg=true").json()
        self.assertGreater(nonveg["count"], 0)
        self.assertGreater(veg["count"], 0)

        fast = client.get("/api/restaurants?max_delivery=25").json()
        self.assertTrue(all(r["delivery_min"] <= 25 for r in fast["restaurants"]))

        self.assertEqual(client.get("/api/restaurants/nope").status_code, 404)

    def test_menu_and_extras(self):
        client = Client()
        menu = client.get("/api/restaurants/pizza-roma").json()
        self.assertTrue(menu["menu"])
        self.assertTrue(menu["categories"])

        popular = client.get("/api/dishes/popular").json()["dishes"]
        self.assertGreater(len(popular), 0)

        cuisines = client.get("/api/cuisines").json()["cuisines"]
        self.assertIn("Pizza", cuisines)

        found = client.get("/api/search?q=biryani").json()
        self.assertTrue(found["restaurants"] or found["dishes"])


class CartAndOrderTests(TestCase):
    def test_cart_coupon_and_checkout(self):
        client = Client()
        dish = client.get("/api/dishes/popular").json()["dishes"][0]

        cart = client.post(
            "/api/cart/items", {"dish_id": dish["id"], "qty": 2}, content_type="application/json"
        ).json()
        self.assertEqual(cart["summary"]["count"], 2)
        self.assertEqual(cart["summary"]["subtotal"], dish["price"] * 2)

        discounted = client.post(
            "/api/cart/coupon", {"code": "WELCOME50"}, content_type="application/json"
        ).json()
        self.assertGreater(discounted["summary"]["discount"], 0)

        placed = client.post(
            "/api/orders",
            {
                "customer_name": "Test Foodie",
                "phone": "9876543210",
                "address": "12 MG Road, Bengaluru",
                "payment_method": "UPI · Google Pay",
                "coupon": "WELCOME50",
            },
            content_type="application/json",
        )
        self.assertEqual(placed.status_code, 200)
        order = placed.json()["order"]
        self.assertTrue(order["code"].startswith("FEX-"))
        self.assertEqual(order["tracking"]["current_index"], 0)
        self.assertEqual(order["payment_method"], "UPI · Google Pay")

        self.assertEqual(client.get("/api/cart").json()["summary"]["count"], 0)
        self.assertEqual(client.get(f"/api/orders/{order['code']}").status_code, 200)
        self.assertEqual(len(client.get("/api/orders").json()["orders"]), 1)

        reordered = client.post(f"/api/orders/{order['code']}/reorder")
        self.assertEqual(reordered.status_code, 200)
        self.assertGreater(reordered.json()["summary"]["count"], 0)

    def test_invalid_coupon(self):
        client = Client()
        dish = client.get("/api/dishes/popular").json()["dishes"][0]
        client.post("/api/cart/items", {"dish_id": dish["id"], "qty": 1}, content_type="application/json")
        res = client.post("/api/cart/coupon", {"code": "NOPE"}, content_type="application/json")
        self.assertEqual(res.status_code, 400)


class AuthTests(TestCase):
    def test_register_login_profile(self):
        client = Client()
        res = client.post(
            "/api/auth/register",
            {"name": "Test User", "email": "tester@example.com", "password": "secret123"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(client.get("/api/auth/me").json()["authenticated"])

        client.post("/api/auth/logout")
        self.assertFalse(client.get("/api/auth/me").json()["authenticated"])

        bad = client.post(
            "/api/auth/login", {"email": "tester@example.com", "password": "wrong"}, content_type="application/json"
        )
        self.assertEqual(bad.status_code, 401)

        ok = client.post(
            "/api/auth/login", {"email": "tester@example.com", "password": "secret123"}, content_type="application/json"
        )
        self.assertEqual(ok.status_code, 200)

        patched = client.patch(
            "/api/auth/me", {"phone": "9000000000"}, content_type="application/json"
        ).json()
        self.assertEqual(patched["user"]["phone"], "9000000000")

    def test_demo_user_password(self):
        from .models import User

        demo = User.objects.get(email="demo@foodieexpress.com")
        self.assertTrue(demo.check_password("foodie123"))


class DineoutTests(TestCase):
    def test_venues_booking_and_cancel(self):
        client = Client()
        venues = client.get("/api/dineout/venues").json()
        self.assertGreaterEqual(venues["count"], 5)
        venue = venues["venues"][0]

        res = client.post(
            "/api/dineout/book",
            {
                "venue_id": venue["id"],
                "guest_name": "Table Tester",
                "phone": "9876500000",
                "guests": 4,
                "date": "2026-02-14",
                "time": "8:00 PM",
                "notes": "Window table",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        booking = res.json()["booking"]
        self.assertTrue(booking["code"].startswith("DINE-"))
        self.assertEqual(booking["venue"], venue["name"])

        lookup = client.get(f"/api/dineout/bookings/lookup?codes={booking['code']}").json()["bookings"]
        self.assertEqual(len(lookup), 1)

        by_phone = client.get("/api/dineout/bookings?phone=9876500000").json()["bookings"]
        self.assertEqual(len(by_phone), 1)

        cancelled = client.post(f"/api/dineout/bookings/{booking['code']}/cancel").json()
        self.assertEqual(cancelled["booking"]["status"], "cancelled")

    def test_partner_lead(self):
        res = Client().post(
            "/api/partner",
            {"restaurant_name": "Spice Hub", "owner_name": "Riya", "phone": "9000000001", "city": "Pune"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["ok"])
