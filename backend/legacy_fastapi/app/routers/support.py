from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PartnerLead

router = APIRouter(prefix="/api", tags=["support"])


class PartnerIn(BaseModel):
    restaurant_name: str = Field(min_length=2, max_length=160)
    owner_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=24)
    email: str = ""
    city: str = ""
    message: str = ""


@router.post("/partner")
def partner_signup(payload: PartnerIn, db: Session = Depends(get_db)):
    lead = PartnerLead(
        restaurant_name=payload.restaurant_name.strip(),
        owner_name=payload.owner_name.strip(),
        phone=payload.phone.strip(),
        email=payload.email.strip(),
        city=payload.city.strip(),
        message=payload.message.strip(),
    )
    db.add(lead)
    db.commit()
    return {"ok": True, "message": "Thanks! Our partnerships team will call you within 24 hours."}
