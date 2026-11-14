from __future__ import annotations

from pydantic import BaseModel, Field


class CartAdd(BaseModel):
    dish_id: int
    qty: int = Field(default=1, ge=1, le=20)


class CartUpdate(BaseModel):
    qty: int = Field(default=1, ge=0, le=20)


class CouponCheck(BaseModel):
    code: str
    subtotal: float = 0


class CheckoutIn(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=24)
    address: str = Field(min_length=5, max_length=255)
    payment_method: str = "UPI"
    notes: str = ""
    coupon: str = ""


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=6, max_length=128)
    phone: str = ""
    address: str = ""


class LoginIn(BaseModel):
    email: str
    password: str


class ProfileIn(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
