from __future__ import annotations

import json
from datetime import timezone as dt_timezone

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    phone = models.CharField(max_length=24, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"

    def set_password(self, raw: str):
        self.password_hash = make_password(raw)

    def check_password(self, raw: str) -> bool:
        return check_password(raw, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone or "",
            "address": self.address or "",
        }

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    cuisine = models.CharField(max_length=160)
    area = models.CharField(max_length=120)
    rating = models.FloatField(default=4.3)
    rating_count = models.IntegerField(default=120)
    delivery_min = models.IntegerField(default=30)
    price_for_two = models.IntegerField(default=400)
    image = models.CharField(max_length=255)
    offer = models.CharField(max_length=120, blank=True, default="")
    accent = models.CharField(max_length=24, default="#FF5A1F")
    badges = models.CharField(max_length=200, blank=True, default="")
    is_promo = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)

    class Meta:
        db_table = "restaurants"
        ordering = ["-rating", "delivery_min"]

    def badge_list(self):
        return [b for b in (self.badges or "").split(",") if b]

    def to_dict(self, with_menu=False):
        data = {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "cuisine": self.cuisine,
            "area": self.area,
            "rating": round(self.rating, 1),
            "rating_count": self.rating_count,
            "delivery_min": self.delivery_min,
            "price_for_two": self.price_for_two,
            "image": self.image,
            "offer": self.offer or "",
            "accent": self.accent,
            "badges": self.badge_list(),
            "is_promo": self.is_promo,
            "is_open": self.is_open,
            "dish_count": self.dishes.count(),
        }
        if with_menu:
            data["menu"] = [d.to_dict() for d in self.dishes.order_by("category", "name")]
        return data

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name="dishes", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255)
    price = models.FloatField()
    veg = models.BooleanField(default=True)
    category = models.CharField(max_length=60, default="Recommended")
    image = models.CharField(max_length=255)
    popular = models.BooleanField(default=False)
    rating = models.FloatField(default=4.4)
    prep_min = models.IntegerField(default=18)

    class Meta:
        db_table = "dishes"
        ordering = ["category", "name"]

    def to_dict(self):
        return {
            "id": self.id,
            "restaurant_id": self.restaurant_id,
            "restaurant_name": self.restaurant.name,
            "restaurant_slug": self.restaurant.slug,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "veg": self.veg,
            "category": self.category,
            "image": self.image,
            "popular": self.popular,
            "rating": round(self.rating, 1),
            "prep_min": self.prep_min,
        }

    def __str__(self):
        return self.name


class CartItem(models.Model):
    sid = models.CharField(max_length=64, db_index=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        ordering = ["created_at"]


class Order(models.Model):
    code = models.CharField(max_length=24, unique=True, db_index=True)
    sid = models.CharField(max_length=64, blank=True, default="", db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=24)
    address = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=40, default="UPI")
    notes = models.CharField(max_length=255, blank=True, default="")
    subtotal = models.FloatField(default=0)
    delivery_fee = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    total = models.FloatField(default=0)
    coupon = models.CharField(max_length=24, blank=True, default="")
    status = models.CharField(max_length=24, default="confirmed")
    eta_min = models.IntegerField(default=32)
    placed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "orders"
        ordering = ["-placed_at"]

    def timeline(self):
        placed = self.placed_at
        if timezone.is_naive(placed):
            placed = placed.replace(tzinfo=dt_timezone.utc)
        elapsed = (timezone.now() - placed).total_seconds() / 60
        stages = [
            ("confirmed", "Order confirmed", "Restaurant accepted your order", 0),
            ("preparing", "Chef is cooking", "Freshly preparing your meal", 3),
            ("out_for_delivery", "On the way", "Rider picked up your order", 12),
            ("delivered", "Delivered", "Enjoy your meal!", self.eta_min),
        ]
        current = 0
        for idx, stage in enumerate(stages):
            if elapsed >= stage[3]:
                current = idx
        return {
            "elapsed_min": round(elapsed, 1),
            "current_index": current,
            "stages": [
                {"key": k, "title": t, "subtitle": s, "at_min": m, "done": i <= current}
                for i, (k, t, s, m) in enumerate(stages)
            ],
            "progress": min(100, int((elapsed / max(self.eta_min, 1)) * 100)),
        }

    def to_dict(self):
        return {
            "code": self.code,
            "customer_name": self.customer_name,
            "phone": self.phone,
            "address": self.address,
            "payment_method": self.payment_method,
            "notes": self.notes or "",
            "subtotal": round(self.subtotal, 2),
            "delivery_fee": round(self.delivery_fee, 2),
            "discount": round(self.discount, 2),
            "total": round(self.total, 2),
            "coupon": self.coupon or "",
            "status": self.status,
            "eta_min": self.eta_min,
            "placed_at": self.placed_at.isoformat(),
            "placed_at_label": timezone.localtime(self.placed_at).strftime("%d %b %Y · %I:%M %p"),
            "items": [
                {"name": i.name, "qty": i.qty, "price": i.price, "image": i.image, "veg": i.veg}
                for i in self.items.all()
            ],
            "tracking": self.timeline(),
        }

    def __str__(self):
        return self.code


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    dish_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=120)
    price = models.FloatField()
    qty = models.IntegerField(default=1)
    image = models.CharField(max_length=255, blank=True, default="")
    veg = models.BooleanField(default=True)

    class Meta:
        db_table = "order_items"


class DineoutVenue(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    cuisine = models.CharField(max_length=160)
    area = models.CharField(max_length=120)
    rating = models.FloatField(default=4.5)
    price_for_two = models.IntegerField(default=900)
    image = models.CharField(max_length=255)
    offer = models.CharField(max_length=120, default="Flat 20% OFF")
    ambiance = models.CharField(max_length=120, default="Fine Dining")
    slots = models.CharField(
        max_length=255,
        default="12:00 PM,1:00 PM,2:00 PM,7:00 PM,8:00 PM,9:00 PM,10:00 PM",
    )
    accent = models.CharField(max_length=24, default="#6d28d9")

    class Meta:
        db_table = "dineout_venues"
        ordering = ["-rating"]

    def slot_list(self):
        return [s.strip() for s in (self.slots or "").split(",") if s.strip()]

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "cuisine": self.cuisine,
            "area": self.area,
            "rating": round(self.rating, 1),
            "price_for_two": self.price_for_two,
            "image": self.image,
            "offer": self.offer,
            "ambiance": self.ambiance,
            "slots": self.slot_list(),
            "accent": self.accent,
        }

    def __str__(self):
        return self.name


class DineoutBooking(models.Model):
    code = models.CharField(max_length=24, unique=True, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    venue = models.ForeignKey(DineoutVenue, related_name="bookings", on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=24)
    email = models.CharField(max_length=180, blank=True, default="")
    guests = models.IntegerField(default=2)
    date = models.CharField(max_length=32)
    time = models.CharField(max_length=32)
    notes = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=24, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dineout_bookings"
        ordering = ["-created_at"]

    def to_dict(self):
        return {
            "code": self.code,
            "venue": self.venue.name,
            "venue_slug": self.venue.slug,
            "image": self.venue.image,
            "guest_name": self.guest_name,
            "phone": self.phone,
            "email": self.email,
            "guests": self.guests,
            "date": self.date,
            "time": self.time,
            "notes": self.notes,
            "status": self.status,
            "offer": self.venue.offer,
            "created_label": timezone.localtime(self.created_at).strftime("%d %b %Y · %I:%M %p"),
        }


class PartnerLead(models.Model):
    restaurant_name = models.CharField(max_length=160)
    owner_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=24)
    email = models.CharField(max_length=180, blank=True, default="")
    city = models.CharField(max_length=80, blank=True, default="")
    message = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partner_leads"
