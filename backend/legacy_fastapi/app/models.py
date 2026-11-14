from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(24))
    address: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone or "",
            "address": self.address or "",
        }


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    cuisine: Mapped[str] = mapped_column(String(160))
    area: Mapped[str] = mapped_column(String(120))
    rating: Mapped[float] = mapped_column(Float, default=4.3)
    rating_count: Mapped[int] = mapped_column(Integer, default=120)
    delivery_min: Mapped[int] = mapped_column(Integer, default=30)
    price_for_two: Mapped[int] = mapped_column(Integer, default=400)
    image: Mapped[str] = mapped_column(String(255))
    offer: Mapped[str | None] = mapped_column(String(120))
    accent: Mapped[str] = mapped_column(String(24), default="#FF5A1F")
    badges: Mapped[str | None] = mapped_column(String(200))
    is_promo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)

    dishes: Mapped[list["Dish"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan", lazy="selectin"
    )

    def to_dict(self, with_menu: bool = False):
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
            "badges": [b for b in (self.badges or "").split(",") if b],
            "is_promo": self.is_promo,
            "is_open": self.is_open,
            "dish_count": len(self.dishes),
        }
        if with_menu:
            data["menu"] = [d.to_dict() for d in sorted(self.dishes, key=lambda d: (d.category, d.name))]
        return data


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    veg: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[str] = mapped_column(String(60), default="Recommended")
    image: Mapped[str] = mapped_column(String(255))
    popular: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float] = mapped_column(Float, default=4.4)
    prep_min: Mapped[int] = mapped_column(Integer, default=18)

    restaurant: Mapped[Restaurant] = relationship(back_populates="dishes")

    def to_dict(self):
        return {
            "id": self.id,
            "restaurant_id": self.restaurant_id,
            "restaurant_name": self.restaurant.name if self.restaurant else "",
            "restaurant_slug": self.restaurant.slug if self.restaurant else "",
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


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sid: Mapped[str] = mapped_column(String(64), index=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    dish: Mapped[Dish] = relationship(lazy="selectin")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    sid: Mapped[str | None] = mapped_column(String(64), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(24))
    address: Mapped[str] = mapped_column(String(255))
    payment_method: Mapped[str] = mapped_column(String(40), default="UPI")
    notes: Mapped[str | None] = mapped_column(String(255))
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    delivery_fee: Mapped[float] = mapped_column(Float, default=0)
    discount: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, default=0)
    coupon: Mapped[str | None] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(24), default="confirmed")
    eta_min: Mapped[int] = mapped_column(Integer, default=32)
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User | None] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )

    def timeline(self):
        elapsed = (utcnow() - self.placed_at.replace(tzinfo=timezone.utc)).total_seconds() / 60
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
                {"key": k, "title": t, "subtitle": s, "at_min": m, "done": idx <= current}
                for idx, (k, t, s, m) in enumerate(stages)
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
            "placed_at_label": self.placed_at.strftime("%d %b %Y · %I:%M %p"),
            "items": [
                {"name": i.name, "qty": i.qty, "price": i.price, "image": i.image, "veg": i.veg}
                for i in self.items
            ],
            "tracking": self.timeline(),
        }


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    dish_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(120))
    price: Mapped[float] = mapped_column(Float)
    qty: Mapped[int] = mapped_column(Integer, default=1)
    image: Mapped[str] = mapped_column(String(255), default="")
    veg: Mapped[bool] = mapped_column(Boolean, default=True)

    order: Mapped[Order] = relationship(back_populates="items")


class DineoutVenue(Base):
    __tablename__ = "dineout_venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    cuisine: Mapped[str] = mapped_column(String(160))
    area: Mapped[str] = mapped_column(String(120))
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    price_for_two: Mapped[int] = mapped_column(Integer, default=900)
    image: Mapped[str] = mapped_column(String(255))
    offer: Mapped[str] = mapped_column(String(120), default="Flat 20% OFF")
    ambiance: Mapped[str] = mapped_column(String(120), default="Fine Dining")
    slots: Mapped[str] = mapped_column(String(255), default="12:00 PM,1:00 PM,2:00 PM,7:00 PM,8:00 PM,9:00 PM,10:00 PM")
    accent: Mapped[str] = mapped_column(String(24), default="#6d28d9")

    bookings: Mapped[list["DineoutBooking"]] = relationship(
        back_populates="venue", cascade="all, delete-orphan"
    )

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


class DineoutBooking(Base):
    __tablename__ = "dineout_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("dineout_venues.id"))
    guest_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(24))
    email: Mapped[str] = mapped_column(String(180), default="")
    guests: Mapped[int] = mapped_column(Integer, default=2)
    date: Mapped[str] = mapped_column(String(32))
    time: Mapped[str] = mapped_column(String(32))
    notes: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(24), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    venue: Mapped[DineoutVenue] = relationship(back_populates="bookings", lazy="selectin")

    def to_dict(self):
        return {
            "code": self.code,
            "venue": self.venue.name if self.venue else "",
            "venue_slug": self.venue.slug if self.venue else "",
            "image": self.venue.image if self.venue else "",
            "guest_name": self.guest_name,
            "phone": self.phone,
            "email": self.email,
            "guests": self.guests,
            "date": self.date,
            "time": self.time,
            "notes": self.notes,
            "status": self.status,
            "offer": self.venue.offer if self.venue else "",
            "created_label": self.created_at.strftime("%d %b %Y · %I:%M %p"),
        }


class PartnerLead(Base):
    __tablename__ = "partner_leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_name: Mapped[str] = mapped_column(String(160))
    owner_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(24))
    email: Mapped[str] = mapped_column(String(180), default="")
    city: Mapped[str] = mapped_column(String(80), default="")
    message: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
