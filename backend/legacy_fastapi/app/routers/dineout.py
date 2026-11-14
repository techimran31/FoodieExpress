from __future__ import annotations

import random
import string

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user
from app.models import DineoutBooking, DineoutVenue, User

router = APIRouter(prefix="/api/dineout", tags=["dineout"])


class BookingIn(BaseModel):
    venue_id: int
    guest_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=24)
    email: str = ""
    guests: int = Field(default=2, ge=1, le=20)
    date: str = Field(min_length=3, max_length=32)
    time: str = Field(min_length=2, max_length=32)
    notes: str = ""


def _code(db: Session) -> str:
    for _ in range(25):
        code = "DINE-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not db.scalar(select(DineoutBooking.id).filter_by(code=code)):
            return code
    raise HTTPException(status_code=500, detail="Could not generate booking code")


@router.get("/venues")
def venues(
    search: str = "",
    ambiance: str = "",
    min_rating: float = 0,
    db: Session = Depends(get_db),
):
    term = search.strip().lower()
    rows = db.execute(select(DineoutVenue).order_by(DineoutVenue.rating.desc())).scalars().all()
    out = []
    for v in rows:
        if min_rating and v.rating < min_rating:
            continue
        if ambiance and ambiance.lower() not in v.ambiance.lower():
            continue
        if term and not (
            term in v.name.lower()
            or term in v.cuisine.lower()
            or term in v.area.lower()
            or term in v.ambiance.lower()
        ):
            continue
        out.append(v.to_dict())
    return {"count": len(out), "venues": out}


@router.post("/book")
def book_table(
    payload: BookingIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user),
):
    venue = db.get(DineoutVenue, payload.venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    booking = DineoutBooking(
        code=_code(db),
        user_id=user.id if user else None,
        venue_id=venue.id,
        guest_name=payload.guest_name.strip(),
        phone=payload.phone.strip(),
        email=payload.email.strip(),
        guests=payload.guests,
        date=payload.date.strip(),
        time=payload.time.strip(),
        notes=payload.notes.strip(),
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {
        "ok": True,
        "message": f"Table booked at {venue.name}!",
        "booking": booking.to_dict(),
    }


@router.get("/bookings")
def my_bookings(phone: str = "", db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    query = select(DineoutBooking).order_by(DineoutBooking.created_at.desc())
    if user:
        query = query.where(DineoutBooking.user_id == user.id)
    elif phone.strip():
        query = query.where(DineoutBooking.phone == phone.strip())
    else:
        return {"bookings": []}
    rows = db.execute(query.limit(20)).scalars().all()
    return {"bookings": [b.to_dict() for b in rows]}


@router.get("/bookings/lookup")
def lookup_bookings(codes: str = "", db: Session = Depends(get_db)):
    """Return bookings for the given comma-separated codes (guest-friendly)."""
    wanted = [c.strip().upper() for c in codes.split(",") if c.strip()][:20]
    if not wanted:
        return {"bookings": []}
    rows = db.execute(
        select(DineoutBooking)
        .where(DineoutBooking.code.in_(wanted))
        .order_by(DineoutBooking.created_at.desc())
    ).scalars().all()
    return {"bookings": [b.to_dict() for b in rows]}


@router.post("/bookings/{code}/cancel")
def cancel_booking(code: str, db: Session = Depends(get_db)):
    booking = db.scalar(select(DineoutBooking).where(DineoutBooking.code == code.upper()))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()
    return {"ok": True, "booking": booking.to_dict()}
