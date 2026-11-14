"""End-to-end API tests. Run from backend/:  python -m pytest -q"""
import os
import pathlib
import tempfile

_TMP_DIR = tempfile.mkdtemp(prefix="foodieexpress-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{pathlib.Path(_TMP_DIR) / 'fe_test.db'}"

from fastapi.testclient import TestClient  # noqa: E402

from app import create_app  # noqa: E402


def make_client():
    return TestClient(create_app())


def test_home_and_pages():
    with make_client() as client:
        for path in ["/", "/index.html", "/restaurants.html", "/cart.html",
                     "/checkout.html", "/orders.html", "/track.html", "/auth.html",
                     "/account.html", "/dineout.html", "/help.html", "/partner.html",
                     "/payments.html", "/restaurant.html"]:
            res = client.get(path)
            assert res.status_code == 200, path
        assert client.get("/assets/css/app.css").status_code == 200


def test_restaurants_and_menu():
    with make_client() as client:
        res = client.get("/api/restaurants")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 10

        slug = data["restaurants"][0]["slug"]
        menu = client.get(f"/api/restaurants/{slug}").json()
        assert menu["menu"] and menu["categories"]

        filtered = client.get("/api/restaurants?cuisine=Pizza").json()
        assert filtered["count"] >= 1

        assert client.get("/api/restaurants/nope").status_code == 404


def test_cart_and_checkout_flow():
    with make_client() as client:
        dish = client.get("/api/dishes/popular").json()["dishes"][0]

        cart = client.post("/api/cart/items", json={"dish_id": dish["id"], "qty": 2}).json()
        assert cart["summary"]["count"] == 2
        assert cart["summary"]["subtotal"] == dish["price"] * 2

        with_coupon = client.post("/api/cart/coupon", json={"code": "WELCOME50"}).json()
        assert with_coupon["summary"]["discount"] > 0

        order = client.post(
            "/api/orders",
            json={
                "customer_name": "Test Foodie",
                "phone": "9876543210",
                "address": "12 MG Road, Bengaluru",
                "payment_method": "UPI",
                "coupon": "WELCOME50",
            },
        )
        assert order.status_code == 200
        body = order.json()["order"]
        assert body["code"].startswith("FEX-")
        assert body["tracking"]["current_index"] == 0

        assert client.get("/api/cart").json()["summary"]["count"] == 0
        assert client.get(f"/api/orders/{body['code']}").status_code == 200
        assert len(client.get("/api/orders").json()["orders"]) >= 1


def test_coupon_validation():
    with make_client() as client:
        dish = client.get("/api/dishes/popular").json()["dishes"][0]
        client.post("/api/cart/items", json={"dish_id": dish["id"], "qty": 1})
        bad = client.post("/api/cart/coupon", json={"code": "NOPE"})
        assert bad.status_code == 400


def test_auth_flow():
    with make_client() as client:
        email = "tester@example.com"
        client.post("/api/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "secret123",
        })
        me = client.get("/api/auth/me").json()
        assert me["authenticated"] is True
        assert me["user"]["email"] == email

        client.post("/api/auth/logout")
        assert client.get("/api/auth/me").json()["authenticated"] is False

        assert client.post("/api/auth/login", json={"email": email, "password": "wrong"}).status_code == 401
        assert client.post("/api/auth/login", json={"email": email, "password": "secret123"}).status_code == 200

        updated = client.patch("/api/auth/me", json={"phone": "9000000000"}).json()
        assert updated["user"]["phone"] == "9000000000"


def test_dineout_booking():
    with make_client() as client:
        data = client.get("/api/dineout/venues").json()
        assert data["count"] >= 5
        venue = data["venues"][0]

        booked = client.post("/api/dineout/book", json={
            "venue_id": venue["id"],
            "guest_name": "Table Tester",
            "phone": "9876500000",
            "guests": 4,
            "date": "2026-02-14",
            "time": "8:00 PM",
            "notes": "Window table",
        })
        assert booked.status_code == 200
        booking = booked.json()["booking"]
        assert booking["code"].startswith("DINE-")
        assert booking["venue"] == venue["name"]

        cancelled = client.post(f"/api/dineout/bookings/{booking['code']}/cancel")
        assert cancelled.json()["booking"]["status"] == "cancelled"


def test_partner_lead():
    with make_client() as client:
        res = client.post("/api/partner", json={
            "restaurant_name": "Spice Hub",
            "owner_name": "Riya",
            "phone": "9000000001",
            "city": "Pune",
        })
        assert res.status_code == 200
        assert res.json()["ok"] is True
