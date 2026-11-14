from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_sid
from app.models import CartItem, Dish
from app.schemas import CartAdd, CartUpdate

router = APIRouter(prefix="/api/cart", tags=["cart"])

FREE_DELIVERY_ABOVE = 499
DELIVERY_FEE = 39
PLATFORM_FEE = 6
TAX_RATE = 0.05

COUPONS = {
    "WELCOME50": {"type": "percent", "value": 50, "cap": 150, "min": 299,
                  "label": "50% off up to ₹150"},
    "FOODIE20": {"type": "percent", "value": 20, "cap": 120, "min": 399,
                 "label": "20% off up to ₹120"},
    "FLAT100": {"type": "flat", "value": 100, "cap": 100, "min": 599,
                "label": "Flat ₹100 off"},
    "FREESHIP": {"type": "shipping", "value": 0, "cap": 0, "min": 199,
                 "label": "Free delivery"},
}


def _coupon_discount(code: str, subtotal: float) -> tuple[float, float]:
    """Returns (item_discount, delivery_discount)."""
    coupon = COUPONS.get((code or "").upper())
    if not coupon or subtotal < coupon["min"]:
        return 0.0, 0.0
    if coupon["type"] == "shipping":
        return 0.0, float(DELIVERY_FEE)
    if coupon["type"] == "flat":
        return min(coupon["value"], subtotal), 0.0
    return min(subtotal * coupon["value"] / 100, coupon["cap"]), 0.0


def cart_payload(db: Session, sid: str, coupon_code: str = "") -> dict:
    rows = db.execute(
        select(CartItem).where(CartItem.sid == sid).order_by(CartItem.created_at.asc())
    ).scalars().all()

    items = []
    subtotal = 0.0
    count = 0
    for row in rows:
        dish = row.dish
        if not dish:
            continue
        line_total = dish.price * row.qty
        subtotal += line_total
        count += row.qty
        items.append(
            {
                "id": row.id,
                "qty": row.qty,
                "line_total": round(line_total, 2),
                "dish": dish.to_dict(),
            }
        )

    discount, shipping_discount = _coupon_discount(coupon_code, subtotal) if items else (0.0, 0.0)
    delivery_fee = 0.0 if subtotal >= FREE_DELIVERY_ABOVE else (DELIVERY_FEE if items else 0.0)
    delivery_fee = max(0.0, delivery_fee - shipping_discount)
    platform_fee = PLATFORM_FEE if items else 0.0
    tax = round((subtotal - discount) * TAX_RATE, 2) if items else 0.0
    total = max(0.0, subtotal - discount + delivery_fee + platform_fee + tax)

    return {
        "items": items,
        "summary": {
            "count": count,
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "delivery_fee": round(delivery_fee, 2),
            "platform_fee": round(platform_fee, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "coupon": (coupon_code or "").upper(),
            "free_delivery_gap": round(max(0.0, FREE_DELIVERY_ABOVE - subtotal), 2),
        },
    }


@router.get("")
def get_cart(request: Request, coupon: str = "", db: Session = Depends(get_db)):
    sid = get_sid(request)
    return cart_payload(db, sid, coupon)


@router.post("/items")
def add_item(payload: CartAdd, request: Request, db: Session = Depends(get_db)):
    sid = get_sid(request)
    dish = db.get(Dish, payload.dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    existing = db.scalar(select(CartItem).where(CartItem.sid == sid, CartItem.dish_id == dish.id))
    if existing:
        existing.qty = min(20, existing.qty + payload.qty)
    else:
        db.add(CartItem(sid=sid, dish_id=dish.id, qty=min(20, payload.qty)))
    db.commit()
    return {"ok": True, **cart_payload(db, sid)}


@router.patch("/items/{item_id}")
def update_item(item_id: int, payload: CartUpdate, request: Request, db: Session = Depends(get_db)):
    sid = get_sid(request)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.sid == sid))
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if payload.qty == 0:
        db.delete(item)
    else:
        item.qty = payload.qty
    db.commit()
    return {"ok": True, **cart_payload(db, sid)}


@router.delete("/items/{item_id}")
def remove_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    sid = get_sid(request)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.sid == sid))
    if item:
        db.delete(item)
        db.commit()
    return {"ok": True, **cart_payload(db, sid)}


@router.delete("")
def clear_cart(request: Request, db: Session = Depends(get_db)):
    sid = get_sid(request)
    for item in db.execute(select(CartItem).where(CartItem.sid == sid)).scalars().all():
        db.delete(item)
    db.commit()
    return {"ok": True, **cart_payload(db, sid)}


@router.post("/coupon")
def apply_coupon(payload: dict, request: Request, db: Session = Depends(get_db)):
    sid = get_sid(request)
    code = str(payload.get("code", "")).strip().upper()
    base = cart_payload(db, sid)
    subtotal = base["summary"]["subtotal"]
    if not code:
        return {"ok": True, "message": "Coupon removed", **base}
    if code not in COUPONS:
        raise HTTPException(status_code=400, detail="That coupon code is not valid")
    coupon = COUPONS[code]
    if subtotal < coupon["min"]:
        raise HTTPException(
            status_code=400,
            detail=f"Add ₹{coupon['min'] - subtotal:.0f} more to use {code}",
        )
    data = cart_payload(db, sid, code)
    return {"ok": True, "message": f"{code} applied · {coupon['label']}", **data}
