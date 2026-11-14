from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Dish, Restaurant

router = APIRouter(prefix="/api", tags=["restaurants"])

SORTS = {
    "recommended": (Restaurant.rating.desc(), Restaurant.delivery_min.asc()),
    "rating": (Restaurant.rating.desc(),),
    "fastest": (Restaurant.delivery_min.asc(),),
    "price_low": (Restaurant.price_for_two.asc(),),
    "price_high": (Restaurant.price_for_two.desc(),),
}


@router.get("/cuisines")
def cuisines(db: Session = Depends(get_db)):
    rows = db.execute(select(Restaurant.cuisine)).scalars().all()
    seen: list[str] = []
    for row in rows:
        for part in (row or "").split(","):
            name = part.strip()
            if name and name not in seen:
                seen.append(name)
    return {"cuisines": sorted(seen)}


@router.get("/restaurants")
def list_restaurants(
    search: str = "",
    cuisine: str = "",
    veg: bool = False,
    nonveg: bool = False,
    promo: bool = False,
    min_rating: float = 0,
    fast: bool = False,
    budget: bool = False,
    max_delivery: int = 0,
    min_price: int = 0,
    max_price: int = 0,
    free: bool = False,
    sort: str = "recommended",
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
):
    query = select(Restaurant)
    term = search.strip().lower()
    if term:
        like = f"%{term}%"
        query = query.where(
            or_(
                func.lower(Restaurant.name).like(like),
                func.lower(Restaurant.cuisine).like(like),
                func.lower(Restaurant.area).like(like),
                func.lower(Restaurant.offer).like(like),
            )
        )
    if cuisine:
        query = query.where(func.lower(Restaurant.cuisine).like(f"%{cuisine.strip().lower()}%"))
    if promo:
        query = query.where(Restaurant.is_promo.is_(True))
    if min_rating:
        query = query.where(Restaurant.rating >= min_rating)
    if fast:
        query = query.where(Restaurant.delivery_min <= 30)
    if budget:
        query = query.where(Restaurant.price_for_two <= 400)
    if max_delivery:
        query = query.where(Restaurant.delivery_min <= max_delivery)
    if min_price:
        query = query.where(Restaurant.price_for_two >= min_price)
    if max_price:
        query = query.where(Restaurant.price_for_two <= max_price)
    if free:
        query = query.where(func.lower(Restaurant.offer).like("%free delivery%"))

    order_by = SORTS.get(sort, SORTS["recommended"])
    query = query.order_by(*order_by).limit(limit)

    restaurants = db.execute(query).scalars().all()

    if veg:
        restaurants = [r for r in restaurants if r.dishes and all(d.veg for d in r.dishes)]
    if nonveg:
        restaurants = [r for r in restaurants if any(not d.veg for d in r.dishes)]

    return {
        "count": len(restaurants),
        "restaurants": [r.to_dict() for r in restaurants],
    }


@router.get("/restaurants/{slug}")
def get_restaurant(slug: str, db: Session = Depends(get_db)):
    restaurant = db.scalar(select(Restaurant).where(Restaurant.slug == slug))
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    data = restaurant.to_dict(with_menu=True)
    data["categories"] = sorted({d["category"] for d in data["menu"]})
    return data


@router.get("/dishes/popular")
def popular_dishes(limit: int = Query(default=8, le=24), db: Session = Depends(get_db)):
    dishes = db.execute(
        select(Dish).where(Dish.popular.is_(True)).order_by(Dish.rating.desc()).limit(limit)
    ).scalars().all()
    return {"dishes": [d.to_dict() for d in dishes]}


@router.get("/search")
def search(q: str = "", db: Session = Depends(get_db)):
    term = q.strip().lower()
    if not term:
        return {"restaurants": [], "dishes": []}
    like = f"%{term}%"
    restaurants = db.execute(
        select(Restaurant)
        .where(or_(func.lower(Restaurant.name).like(like), func.lower(Restaurant.cuisine).like(like)))
        .limit(5)
    ).scalars().all()
    dishes = db.execute(
        select(Dish).where(func.lower(Dish.name).like(like)).order_by(Dish.rating.desc()).limit(6)
    ).scalars().all()
    return {
        "restaurants": [r.to_dict() for r in restaurants],
        "dishes": [d.to_dict() for d in dishes],
    }
