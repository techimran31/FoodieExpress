from __future__ import annotations

import json
import random
import string

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import (
    CartItem,
    Dish,
    DineoutBooking,
    DineoutVenue,
    Order,
    OrderItem,
    PartnerLead,
    Restaurant,
    User,
)
from .services import COUPONS, cart_payload


# ------------------------------------------------------------------ helpers
def json_body(request) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}


def error(message: str, status: int = 400):
    return JsonResponse({"detail": message}, status=status)


def get_sid(request, create: bool = True):
    sid = request.session.get("sid")
    if not sid and create:
        sid = random.getrandbits(64).to_bytes(8, "big").hex()
        request.session["sid"] = sid
    return sid


def current_user(request):
    uid = request.session.get("user_id")
    if not uid:
        return None
    return User.objects.filter(pk=uid).first()


def new_code(prefix: str, model, length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(30):
        code = prefix + "".join(random.choices(alphabet, k=length))
        if not model.objects.filter(code=code).exists():
            return code
    raise RuntimeError("could not generate a unique code")


# ------------------------------------------------------------------ health
def health(request):
    return JsonResponse({"status": "ok", "service": "foodieexpress"})


# ------------------------------------------------------------------ restaurants
def restaurant_list(request):
    search = request.GET.get("search", "").strip().lower()
    cuisine = request.GET.get("cuisine", "").strip().lower()
    veg = request.GET.get("veg", "").lower() in ("true", "1")
    nonveg = request.GET.get("nonveg", "").lower() in ("true", "1")
    promo = request.GET.get("promo", "").lower() in ("true", "1")
    free = request.GET.get("free", "").lower() in ("true", "1")
    min_rating = float(request.GET.get("min_rating") or 0)
    fast = request.GET.get("fast", "").lower() in ("true", "1")
    budget = request.GET.get("budget", "").lower() in ("true", "1")
    max_delivery = int(request.GET.get("max_delivery") or 0)
    min_price = int(request.GET.get("min_price") or 0)
    max_price = int(request.GET.get("max_price") or 0)
    sort = request.GET.get("sort", "recommended")

    qs = Restaurant.objects.all()
    if search:
        from django.db.models import Q

        qs = qs.filter(
            Q(name__icontains=search)
            | Q(cuisine__icontains=search)
            | Q(area__icontains=search)
            | Q(offer__icontains=search)
        )
    if cuisine:
        qs = qs.filter(cuisine__icontains=cuisine)
    if promo:
        qs = qs.filter(is_promo=True)
    if free:
        qs = qs.filter(offer__icontains="free delivery")
    if min_rating:
        qs = qs.filter(rating__gte=min_rating)
    if fast:
        qs = qs.filter(delivery_min__lte=30)
    if budget:
        qs = qs.filter(price_for_two__lte=400)
    if max_delivery:
        qs = qs.filter(delivery_min__lte=max_delivery)
    if min_price:
        qs = qs.filter(price_for_two__gte=min_price)
    if max_price:
        qs = qs.filter(price_for_two__lte=max_price)

    ordering = {
        "recommended": ("-rating", "delivery_min"),
        "rating": ("-rating",),
        "fastest": ("delivery_min",),
        "price_low": ("price_for_two",),
        "price_high": ("-price_for_two",),
    }.get(sort, ("-rating", "delivery_min"))
    restaurants = list(qs.order_by(*ordering)[:100])

    if veg:
        restaurants = [r for r in restaurants if r.dishes.exists() and not r.dishes.filter(veg=False).exists()]
    if nonveg:
        restaurants = [r for r in restaurants if r.dishes.filter(veg=False).exists()]

    return JsonResponse({"count": len(restaurants), "restaurants": [r.to_dict() for r in restaurants]})


def restaurant_detail(request, slug: str):
    restaurant = Restaurant.objects.filter(slug=slug).first()
    if not restaurant:
        return error("Restaurant not found", 404)
    data = restaurant.to_dict(with_menu=True)
    data["categories"] = sorted({d["category"] for d in data["menu"]})
    return JsonResponse(data)


def popular_dishes(request):
    limit = min(int(request.GET.get("limit") or 8), 24)
    dishes = Dish.objects.filter(popular=True).select_related("restaurant").order_by("-rating")[:limit]
    return JsonResponse({"dishes": [d.to_dict() for d in dishes]})


def cuisines(request):
    seen = set()
    for cuisine in Restaurant.objects.values_list("cuisine", flat=True):
        for part in (cuisine or "").split(","):
            name = part.strip()
            if name:
                seen.add(name)
    return JsonResponse({"cuisines": sorted(seen)})


def search(request):
    term = request.GET.get("q", "").strip().lower()
    if not term:
        return JsonResponse({"restaurants": [], "dishes": []})
    from django.db.models import Q

    restaurants = Restaurant.objects.filter(
        Q(name__icontains=term) | Q(cuisine__icontains=term)
    ).order_by("-rating")[:5]
    dishes = Dish.objects.filter(Q(name__icontains=term) | Q(description__icontains=term))         .select_related("restaurant").order_by("-rating")[:6]
    return JsonResponse(
        {
            "restaurants": [r.to_dict() for r in restaurants],
            "dishes": [d.to_dict() for d in dishes],
        }
    )


# ------------------------------------------------------------------ cart
@csrf_exempt
def cart_detail(request):
    sid = get_sid(request)
    if request.method == "GET":
        return JsonResponse(cart_payload(sid, request.GET.get("coupon", "")))
    if request.method == "DELETE":
        CartItem.objects.filter(sid=sid).delete()
        return JsonResponse({"ok": True, **cart_payload(sid)})
    return error("Method not allowed", 405)


@csrf_exempt
def cart_items(request):
    sid = get_sid(request)
    if request.method != "POST":
        return error("Method not allowed", 405)

    data = json_body(request)
    dish = Dish.objects.filter(pk=data.get("dish_id")).first()
    if not dish:
        return error("Dish not found", 404)

    qty = max(1, min(int(data.get("qty", 1)), 20))
    item = CartItem.objects.filter(sid=sid, dish=dish).first()
    if item:
        item.qty = min(20, item.qty + qty)
        item.save(update_fields=["qty"])
    else:
        CartItem.objects.create(sid=sid, dish=dish, qty=qty)
    return JsonResponse({"ok": True, **cart_payload(sid)})


@csrf_exempt
def cart_item_detail(request, item_id: int):
    sid = get_sid(request)
    item = CartItem.objects.filter(pk=item_id, sid=sid).first()
    if not item:
        return error("Cart item not found", 404)

    if request.method == "PATCH":
        qty = int(json_body(request).get("qty", 1))
        if qty <= 0:
            item.delete()
        else:
            item.qty = min(qty, 20)
            item.save(update_fields=["qty"])
        return JsonResponse({"ok": True, **cart_payload(sid)})

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"ok": True, **cart_payload(sid)})

    return error("Method not allowed", 405)


@csrf_exempt
def cart_coupon(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    sid = get_sid(request)
    code = str(json_body(request).get("code", "")).strip().upper()
    base = cart_payload(sid)
    if not code:
        return JsonResponse({"ok": True, "message": "Coupon removed", **base})

    coupon = COUPONS.get(code)
    if not coupon:
        return error("That coupon code is not valid")
    subtotal = base["summary"]["subtotal"]
    if subtotal < coupon["min"]:
        return error(f"Add ₹{coupon['min'] - subtotal:.0f} more to use {code}")

    return JsonResponse({"ok": True, "message": f"{code} applied · {coupon['label']}", **cart_payload(sid, code)})


def cart_count(request):
    sid = get_sid(request, create=False)
    count = sum(CartItem.objects.filter(sid=sid).values_list("qty", flat=True)) if sid else 0
    return JsonResponse({"count": count})


# ------------------------------------------------------------------ orders
@csrf_exempt
def orders(request):
    sid = get_sid(request, create=False)

    if request.method == "GET":
        user = current_user(request)
        qs = Order.objects.all()
        if user:
            qs = qs.filter(user=user) | qs.filter(sid=sid)
        elif sid:
            qs = qs.filter(sid=sid)
        else:
            return JsonResponse({"orders": []})
        return JsonResponse({"orders": [o.to_dict() for o in qs.distinct()[:30]]})

    if request.method != "POST":
        return error("Method not allowed", 405)

    data = json_body(request)
    sid = get_sid(request)
    payload = cart_payload(sid, data.get("coupon", ""))
    if not payload["items"]:
        return error("Your cart is empty")

    name = str(data.get("customer_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    address = str(data.get("address", "")).strip()
    if len(name) < 2 or len(phone) < 6 or len(address) < 5:
        return error("Please provide a valid name, phone and address")

    summary = payload["summary"]
    user = current_user(request)
    order = Order.objects.create(
        code=new_code("FEX-", Order),
        sid=sid,
        user=user,
        customer_name=name,
        phone=phone,
        address=address,
        payment_method=str(data.get("payment_method") or "UPI"),
        notes=str(data.get("notes") or ""),
        subtotal=summary["subtotal"],
        delivery_fee=summary["delivery_fee"],
        discount=summary["discount"],
        total=summary["total"],
        coupon=summary["coupon"],
        eta_min=26 + random.randint(0, 8),
    )
    for item in payload["items"]:
        dish = item["dish"]
        OrderItem.objects.create(
            order=order,
            dish_id=dish["id"],
            name=dish["name"],
            price=dish["price"],
            qty=item["qty"],
            image=dish["image"],
            veg=dish["veg"],
        )

    CartItem.objects.filter(sid=sid).delete()
    if user and not user.address:
        user.address = address
        user.phone = user.phone or phone
        user.save(update_fields=["address", "phone"])

    return JsonResponse({"ok": True, "order": order.to_dict()})


def order_detail(request, code: str):
    order = Order.objects.filter(code=code.upper()).first()
    if not order:
        return error("Order not found", 404)
    return JsonResponse(order.to_dict())


@csrf_exempt
def order_cancel(request, code: str):
    order = Order.objects.filter(code=code.upper()).first()
    if not order:
        return error("Order not found", 404)
    if order.timeline()["current_index"] >= 2:
        return error("Order is already on the way")
    order.status = "cancelled"
    order.save(update_fields=["status"])
    return JsonResponse({"ok": True, "order": order.to_dict()})


@csrf_exempt
def order_reorder(request, code: str):
    order = Order.objects.filter(code=code.upper()).first()
    if not order:
        return error("Order not found", 404)
    sid = get_sid(request)
    for item in order.items.all():
        if not item.dish_id:
            continue
        existing = CartItem.objects.filter(sid=sid, dish_id=item.dish_id).first()
        if existing:
            existing.qty = min(20, existing.qty + item.qty)
            existing.save(update_fields=["qty"])
        else:
            CartItem.objects.create(sid=sid, dish_id=item.dish_id, qty=item.qty)
    return JsonResponse({"ok": True, **cart_payload(sid)})


# ------------------------------------------------------------------ auth
@csrf_exempt
def register(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    data = json_body(request)
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(name) < 2:
        return error("Please enter your name")
    if "@" not in email:
        return error("Please enter a valid email")
    if len(password) < 6:
        return error("Password must be at least 6 characters")
    if User.objects.filter(email=email).exists():
        return error("An account with this email already exists")

    user = User(
        name=name,
        email=email,
        phone=str(data.get("phone", "")).strip(),
        address=str(data.get("address", "")).strip(),
    )
    user.set_password(password)
    user.save()

    request.session["user_id"] = user.id
    return JsonResponse({"ok": True, "user": user.to_dict()})


@csrf_exempt
def login(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    data = json_body(request)
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = User.objects.filter(email=email).first()
    if not user or not user.check_password(password):
        return error("Incorrect email or password", 401)

    request.session["user_id"] = user.id
    return JsonResponse({"ok": True, "user": user.to_dict()})


@csrf_exempt
def logout(request):
    request.session.pop("user_id", None)
    return JsonResponse({"ok": True})


@csrf_exempt
def me(request):
    user = current_user(request)
    if request.method == "GET":
        return JsonResponse({"authenticated": bool(user), "user": user.to_dict() if user else None})

    if request.method == "PATCH":
        if not user:
            return error("Please sign in first", 401)
        data = json_body(request)
        if data.get("name"):
            user.name = str(data["name"]).strip()
        if data.get("phone") is not None:
            user.phone = str(data["phone"]).strip()
        if data.get("address") is not None:
            user.address = str(data["address"]).strip()
        user.save()
        return JsonResponse({"ok": True, "user": user.to_dict()})

    return error("Method not allowed", 405)


# ------------------------------------------------------------------ dineout
def dineout_venues(request):
    search = request.GET.get("search", "").strip().lower()
    ambiance = request.GET.get("ambiance", "").strip().lower()
    min_rating = float(request.GET.get("min_rating") or 0)

    venues = []
    for v in DineoutVenue.objects.all():
        if min_rating and v.rating < min_rating:
            continue
        if ambiance and ambiance not in v.ambiance.lower():
            continue
        if search and not (
            search in v.name.lower()
            or search in v.cuisine.lower()
            or search in v.area.lower()
            or search in v.ambiance.lower()
        ):
            continue
        venues.append(v.to_dict())
    return JsonResponse({"count": len(venues), "venues": venues})


@csrf_exempt
def dineout_book(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    data = json_body(request)

    venue = DineoutVenue.objects.filter(pk=data.get("venue_id")).first()
    if not venue:
        return error("Venue not found", 404)

    guest_name = str(data.get("guest_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    date = str(data.get("date", "")).strip()
    time = str(data.get("time", "")).strip()
    if not guest_name or not phone:
        return error("Guest name and phone number are required")
    if not date or not time:
        return error("Please choose a date and time slot")

    booking = DineoutBooking.objects.create(
        code=new_code("DINE-", DineoutBooking, 5),
        user=current_user(request),
        venue=venue,
        guest_name=guest_name,
        phone=phone,
        email=str(data.get("email", "")).strip(),
        guests=max(1, min(int(data.get("guests", 2)), 20)),
        date=date,
        time=time,
        notes=str(data.get("notes", "")).strip(),
    )
    return JsonResponse(
        {"ok": True, "message": f"Table booked at {venue.name}!", "booking": booking.to_dict()}
    )


def dineout_bookings(request):
    user = current_user(request)
    phone = request.GET.get("phone", "").strip()
    qs = DineoutBooking.objects.select_related("venue").all()
    if user:
        qs = qs.filter(user=user)
    elif phone:
        qs = qs.filter(phone=phone)
    else:
        return JsonResponse({"bookings": []})
    return JsonResponse({"bookings": [b.to_dict() for b in qs[:20]]})


def dineout_lookup(request):
    codes = [c.strip().upper() for c in request.GET.get("codes", "").split(",") if c.strip()][:20]
    if not codes:
        return JsonResponse({"bookings": []})
    qs = DineoutBooking.objects.select_related("venue").filter(code__in=codes)
    return JsonResponse({"bookings": [b.to_dict() for b in qs]})


@csrf_exempt
def dineout_cancel(request, code: str):
    booking = DineoutBooking.objects.filter(code=code.upper()).first()
    if not booking:
        return error("Booking not found", 404)
    booking.status = "cancelled"
    booking.save(update_fields=["status"])
    return JsonResponse({"ok": True, "booking": booking.to_dict()})


# ------------------------------------------------------------------ partner
@csrf_exempt
def partner(request):
    if request.method != "POST":
        return error("Method not allowed", 405)
    data = json_body(request)
    name = str(data.get("restaurant_name", "")).strip()
    owner = str(data.get("owner_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    if len(name) < 2 or len(owner) < 2 or len(phone) < 6:
        return error("Please fill in restaurant name, your name and phone")

    PartnerLead.objects.create(
        restaurant_name=name,
        owner_name=owner,
        phone=phone,
        email=str(data.get("email", "")).strip(),
        city=str(data.get("city", "")).strip(),
        message=str(data.get("message", "")).strip(),
    )
    return JsonResponse({"ok": True, "message": "Thanks! Our partnerships team will call you within 24 hours."})
