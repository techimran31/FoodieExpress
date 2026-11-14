from django.urls import path

from . import views

urlpatterns = [
    # system
    path("health", views.health),
    # restaurants
    path("restaurants", views.restaurant_list),
    path("restaurants/<slug:slug>", views.restaurant_detail),
    path("dishes/popular", views.popular_dishes),
    path("cuisines", views.cuisines),
    path("search", views.search),
    # cart
    path("cart", views.cart_detail),
    path("cart/items", views.cart_items),
    path("cart/items/<int:item_id>", views.cart_item_detail),
    path("cart/coupon", views.cart_coupon),
    path("cart-count", views.cart_count),
    # orders
    path("orders", views.orders),
    path("orders/<str:code>", views.order_detail),
    path("orders/<str:code>/cancel", views.order_cancel),
    path("orders/<str:code>/reorder", views.order_reorder),
    # auth
    path("auth/register", views.register),
    path("auth/login", views.login),
    path("auth/logout", views.logout),
    path("auth/me", views.me),
    # dineout
    path("dineout/venues", views.dineout_venues),
    path("dineout/book", views.dineout_book),
    path("dineout/bookings", views.dineout_bookings),
    path("dineout/bookings/lookup", views.dineout_lookup),
    path("dineout/bookings/<str:code>/cancel", views.dineout_cancel),
    # partner
    path("partner", views.partner),
]
