"""Session helpers: cart SID and signed-in user."""
from __future__ import annotations

import uuid

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User


def get_sid(request: Request, create: bool = True) -> str | None:
    sid = request.session.get("sid")
    if not sid and create:
        sid = uuid.uuid4().hex
        request.session["sid"] = sid
    return sid


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    uid = request.session.get("user_id")
    if not uid:
        return None
    user = db.get(User, int(uid))
    return user
