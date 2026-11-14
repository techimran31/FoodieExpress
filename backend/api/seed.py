from __future__ import annotations

import json
from pathlib import Path

from .models import Dish, DineoutVenue, PartnerLead, Restaurant, User  # noqa: F401

DATA_FILE = Path(__file__).resolve().parent / "data" / "seed.json"


def seed_all(force: bool = False) -> None:
    """Populate restaurants, dishes, dineout venues and the demo user once."""
    if Restaurant.objects.exists() and not force:
        return

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    for r in data["restaurants"]:
        restaurant, _ = Restaurant.objects.get_or_create(
            slug=r["slug"],
            defaults={
                "name": r["name"],
                "cuisine": r["cuisine"],
                "area": r["area"],
                "rating": r["rating"],
                "rating_count": r["rating_count"],
                "delivery_min": r["delivery_min"],
                "price_for_two": r["price_for_two"],
                "image": r["image"],
                "offer": r["offer"],
                "accent": r.get("accent", "#FF5A1F"),
                "badges": r.get("badges", ""),
                "is_promo": r.get("is_promo", False),
            },
        )
        if restaurant.dishes.exists():
            continue
        for (name, desc, price, veg, category, image, popular, rating, prep) in data["menus"][r["slug"]]:
            Dish.objects.create(
                restaurant=restaurant,
                name=name,
                description=desc,
                price=float(price),
                veg=veg,
                category=category,
                image=image,
                popular=popular,
                rating=rating,
                prep_min=prep,
            )

    for v in data["dineout"]:
        DineoutVenue.objects.get_or_create(
            slug=v["slug"],
            defaults={
                "name": v["name"],
                "cuisine": v["cuisine"],
                "area": v["area"],
                "rating": v["rating"],
                "price_for_two": v["price_for_two"],
                "image": v["image"],
                "offer": v["offer"],
                "ambiance": v["ambiance"],
                "accent": v["accent"],
            },
        )

    demo = data["demo_user"]
    user, created = User.objects.get_or_create(
        email=demo["email"],
        defaults={"name": demo["name"], "phone": demo["phone"], "address": demo["address"]},
    )
    if created:
        user.set_password(demo["password"])
        user.save(update_fields=["password_hash"])
