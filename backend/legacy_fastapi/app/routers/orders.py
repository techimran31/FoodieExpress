from __future__ import annotations

import random
import string

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user, get_sid
from app.models import CartItem, Order, OrderItem, User
from app.routers.cart import cart_payload
from app.schemas import CheckoutIn

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _new_code(db: Session) -> str:
    for _ in range(20):
        code = "FEX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.scalar(select(Order.id).filter_by(code=code)):
            return code
    raise HTTPException(status_code=500, detail="Could not generate order code")


@router.post("")
def place_order(
    payload: CheckoutIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user),
):
    sid = get_sid(request)
    cart = cart_payload(db, sid, payload.coupon)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    summary = cart["summary"]
    eta = 26 + random.randint(0, 8)

    order = Order(
        code=_new_code(db),
        sid=sid,
        user_id=user.id if user else None,
        customer_name=payload.customer_name.strip(),
        phone=payload.phone.strip(),
        address=payload.address.strip(),
        payment_method=payload.payment_method,
        notes=payload.notes.strip(),
        subtotal=summary["subtotal"],
        delivery_fee=summary["delivery_fee"],
        discount=summary["discount"],
        total=summary["total"],
        coupon=summary["coupon"],
        status="confirmed",
        eta_min=eta,
    )
    db.add(order)
    db.flush()

    for item in cart["items"]:
        dish = item["dish"]
        db.add(
            OrderItem(
                order_id=order.id,
                dish_id=dish["id"],
                name=dish["name"],
                price=dish["price"],
                qty=item["qty"],
                image=dish["image"],
                veg=dish["veg"],
            )
        )

    for item in db.execute(select(CartItem).where(CartItem.sid == sid)).scalars().all():
        db.delete(item)

    if user:
        user.phone = user.phone or order.phone
        user.address = order.address

    db.commit()
    db.refresh(order)
    return {"ok": True, "order": order.to_dict()}


@router.get("")
def list_orders(request: Request, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    sid = get_sid(request, create=False)
    query = select(Order).order_by(Order.placed_at.desc())
    if user:
        query = query.where((Order.user_id == user.id) | (Order.sid == sid))
    elif sid:
        query = query.where(Order.sid == sid)
    else:
        return {"orders": []}
    orders = db.execute(query.limit(30)).scalars().all()
    return {"orders": [o.to_dict() for o in orders]}


@router.get("/{code}")
def get_order(code: str, db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.code == code.upper()))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_dict()


@router.post("/{code}/cancel")
def cancel_order(code: str, db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.code == code.upper()))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.timeline()["current_index"] >= 2:
        raise HTTPException(status_code=400, detail="Order is already on the way")
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return {"ok": True, "order": order.to_dict()}


@router.post("/{code}/reorder")
def reorder(code: str, request: Request, db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.code == code.upper()))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    sid = get_sid(request)
    for item in order.items:
        if not item.dish_id:
            continue
        existing = db.scalar(select(CartItem).where(CartItem.sid == sid, CartItem.dish_id == item.dish_id))
        if existing:
            existing.qty = min(20, existing.qty + item.qty)
        else:
            db.add(CartItem(sid=sid, dish_id=item.dish_id, qty=item.qty))
    db.commit()
    return {"ok": True, **cart_payload(db, sid)}
