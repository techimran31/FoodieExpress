"""FoodieExpress — FastAPI food delivery backend."""
from __future__ import annotations

import mimetypes
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.db import Base, engine
from app.seed import seed_database, seed_dineout

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

SECRET_KEY = os.environ.get("SECRET_KEY", "foodieexpress-dev-secret-change-me")

# A few bundled food photos use non-standard extensions; map them to image types.
mimetypes.add_type("image/jpeg", ".jpg_compressed")
mimetypes.add_type("image/png", ".png_compressed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    seed_dineout()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="FoodieExpress API",
        description="Restaurants, menus, cart, checkout and live order tracking.",
        version="2.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.routers import auth, cart, dineout, orders, restaurants, support

    app.include_router(restaurants.router)
    app.include_router(cart.router)
    app.include_router(orders.router)
    app.include_router(auth.router)
    app.include_router(dineout.router)
    app.include_router(support.router)

    @app.get("/api/health", tags=["system"])
    def health():
        return {"status": "ok", "service": "foodieexpress"}

    # Clean URLs -> static page (query string preserved)
    from fastapi.responses import RedirectResponse

    for clean, target in {
        "/restaurants": "/restaurants.html",
        "/menu": "/restaurant.html",
        "/cart": "/cart.html",
        "/checkout": "/checkout.html",
        "/payments": "/payments.html",
        "/orders": "/orders.html",
        "/track": "/track.html",
        "/auth": "/auth.html",
        "/login": "/auth.html",
        "/signup": "/auth.html?mode=signup",
        "/account": "/account.html",
        "/dineout": "/dineout.html",
        "/help": "/help.html",
        "/partner": "/partner.html",
    }.items():
        def _redirect(request: Request, target=target):
            query = request.url.query
            return RedirectResponse(f"{target}?{query}" if query else target, status_code=307)

        app.add_api_route(clean, _redirect, methods=["GET"], include_in_schema=False)

    assets = FRONTEND_DIR / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    if FRONTEND_DIR.is_dir():
        app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

    return app


app = create_app()
