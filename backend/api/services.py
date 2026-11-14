from __future__ import annotations

from .models import CartItem

FREE_DELIVERY_ABOVE = 499
DELIVERY_FEE = 39
PLATFORM_FEE = 6
TAX_RATE = 0.05

COUPONS = {
    "WELCOME50": {"type": "percent", "value": 50, "cap": 150, "min": 299, "label": "50% off up to ₹150"},
    "FOODIE20": {"type": "percent", "value": 20, "cap": 120, "min": 399, "label": "20% off up to ₹120"},
    "FLAT100": {"type": "flat", "value": 100, "cap": 100, "min": 599, "label": "Flat ₹100 off"},
    "FREESHIP": {"type": "shipping", "value": 0, "cap": 0, "min": 199, "label": "Free delivery"},
}


def coupon_discount(code: str, subtotal: float) -> tuple[float, float]:
    """Return (item_discount, delivery_discount)."""
    coupon = COUPONS.get((code or "").upper())
    if not coupon or subtotal < coupon["min"]:
        return 0.0, 0.0
    if coupon["type"] == "shipping":
        return 0.0, float(DELIVERY_FEE)
    if coupon["type"] == "flat":
        return min(coupon["value"], subtotal), 0.0
    return min(subtotal * coupon["value"] / 100, coupon["cap"]), 0.0


def cart_payload(sid: str, coupon_code: str = "") -> dict:
    rows = (
        CartItem.objects.filter(sid=sid)
        .select_related("dish", "dish__restaurant")
        .order_by("created_at")
    )

    items = []
    subtotal = 0.0
    count = 0
    for row in rows:
        dish = row.dish
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

    if items:
        discount, shipping_discount = coupon_discount(coupon_code, subtotal)
    else:
        discount, shipping_discount = 0.0, 0.0

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
