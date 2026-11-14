"""Serve the static FoodieExpress website from ../frontend."""
from __future__ import annotations

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.urls import re_path
from django.views.static import serve

FRONTEND_DIR = settings.FRONTEND_DIR

# clean URL -> html file
CLEAN_URLS = {
    "restaurants": "restaurants.html",
    "menu": "restaurant.html",
    "cart": "cart.html",
    "checkout": "checkout.html",
    "payments": "payments.html",
    "orders": "orders.html",
    "track": "track.html",
    "dineout": "dineout.html",
    "help": "help.html",
    "partner": "partner.html",
    "account": "account.html",
    "auth": "auth.html",
    "login": "auth.html",
    "signup": "auth.html?mode=signup",
}


def serve_page(request, name: str):
    path = FRONTEND_DIR / name
    if not path.is_file():
        raise Http404("Page not found")
    return FileResponse(open(path, "rb"), content_type="text/html; charset=utf-8")


def index(request):
    return serve_page(request, "index.html")


def redirect_clean(request, target: str):
    query = request.META.get("QUERY_STRING", "")
    if not query:
        return HttpResponseRedirect(target)
    joiner = "&" if "?" in target else "?"
    return HttpResponseRedirect(f"{target}{joiner}{query}")


def clean(request, key: str):
    return redirect_clean(request, CLEAN_URLS[key])


urlpatterns = [re_path(r"^$", index)]

for _key, _target in CLEAN_URLS.items():
    urlpatterns.append(re_path(rf"^{_key}/?$", clean, {"key": _key}))

# assets (CSS / JS / images) — served by Django so the site also works in
# tests and without a separate web server.
urlpatterns.append(
    re_path(r"^assets/(?P<path>.*)$", serve, {"document_root": settings.FRONTEND_DIR / "assets"})
)

urlpatterns.append(re_path(r"^(?P<name>[A-Za-z0-9_-]+\.html)$", serve_page))
