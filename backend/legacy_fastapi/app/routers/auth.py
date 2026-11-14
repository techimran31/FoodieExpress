from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user
from app.models import User
from app.schemas import LoginIn, ProfileIn, RegisterIn
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.scalar(select(User.id).filter_by(email=email)):
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        phone=payload.phone.strip(),
        address=payload.address.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return {"ok": True, "user": user.to_dict()}


@router.post("/login")
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.scalar(select(User).filter_by(email=email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    request.session["user_id"] = user.id
    return {"ok": True, "user": user.to_dict()}


@router.post("/logout")
def logout(request: Request):
    request.session.pop("user_id", None)
    return {"ok": True}


@router.get("/me")
def me(user: User | None = Depends(current_user)):
    return {"authenticated": bool(user), "user": user.to_dict() if user else None}


@router.patch("/me")
def update_me(payload: ProfileIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Please sign in first")
    if payload.name:
        user.name = payload.name.strip()
    if payload.phone is not None:
        user.phone = payload.phone.strip()
    if payload.address is not None:
        user.address = payload.address.strip()
    db.commit()
    db.refresh(user)
    return {"ok": True, "user": user.to_dict()}
