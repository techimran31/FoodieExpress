"""Seed the database with demo restaurants, menus and a demo account."""
from __future__ import annotations

from urllib.parse import quote

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Dish, Restaurant, User
from app.security import hash_password

FOOD_DIR = "/assets/img/food/"


def img(filename: str) -> str:
    return FOOD_DIR + quote(filename)


# (restaurant, [dishes]) — dish = (name, description, price, veg, category, image, popular, rating, prep)
def _menu(slug: str):
    return MENUS[slug]


MENUS: dict[str, list[tuple]] = {
    "pizza-roma": [
        ("Margherita Pizza", "San Marzano sauce, fresh mozzarella, hand-torn basil", 249, True, "Pizza", "margherita pizza.avif", True, 4.7, 18),
        ("Farmhouse Veg Pizza", "Capsicum, onion, corn, olives and extra cheese", 329, True, "Pizza", "fresh veg pizza.avif", True, 4.6, 20),
        ("Corn & Cheese Pizza", "Golden corn, mozzarella and a hint of oregano", 299, True, "Pizza", "corn pizza.avif", False, 4.4, 18),
        ("Onion Capsicum Pizza", "Crunchy onions with smoky roasted peppers", 279, True, "Pizza", "onion pizza.avif", False, 4.3, 18),
        ("Tikka Chicken Pizza", "Tandoori chicken tikka, onion and mint drizzle", 399, False, "Pizza", "tikka chicken pizza.avif", True, 4.8, 22),
        ("BBQ Chicken Pizza", "Smoky barbeque sauce, grilled chicken, red onion", 419, False, "Pizza", "bbq pizza.avif", False, 4.6, 22),
        ("Chicken 65 Pizza", "Spicy Chicken 65, mozzarella and curry leaves", 429, False, "Pizza", "chicken 65 pizza.avif", False, 4.5, 22),
        ("Garlic Breadsticks", "Buttery garlic bread with a cheesy dip", 149, True, "Sides", "biskets.avif", True, 4.5, 10),
        ("Choco Lava Cake", "Molten chocolate centre, served warm", 129, True, "Desserts", "chocolate milkshake.avif", False, 4.4, 12),
    ],
    "burger-hub": [
        ("Crispy Chicken Burger", "Buttermilk-fried chicken, slaw, chipotle mayo", 229, False, "Burgers", "chiken burger.avif", True, 4.7, 16),
        ("Paneer Tikka Burger", "Charred paneer tikka with mint aioli", 199, True, "Burgers", "paneer burger.avif", True, 4.5, 15),
        ("Pure Veg Burger", "Crunchy veg patty, lettuce and tangy sauce", 159, True, "Burgers", "pure veg burger.avif", False, 4.2, 14),
        ("Chicken 65 Bites", "Crispy spicy chicken poppers with dip", 249, False, "Sides", "chicken 65.avif", True, 4.6, 15),
        ("Chilli Chicken Fries", "Loaded fries with chilli chicken and cheese", 229, False, "Sides", "chilli chicken.avif", False, 4.4, 14),
        ("Veg Spring Rolls", "Crisp rolls stuffed with Asian veggies", 179, True, "Sides", "veg spring rolls.avif", False, 4.3, 12),
        ("Chicken Kebab Roll", "Smoky kebab wrapped in flaky paratha", 199, False, "Wraps", "chicken kebab roll.avif", True, 4.5, 14),
        ("Oreo Milkshake", "Thick cookies-and-cream shake", 149, True, "Shakes", "oreo milkshake.avif", False, 4.6, 8),
    ],
    "biryani-nawab": [
        ("Chicken Dum Biryani", "Slow-cooked long grain rice, saffron and tender chicken", 329, False, "Biryani", "chicken dum biryani.avif", True, 4.9, 30),
        ("Mutton Dum Biryani", "Aged basmati layered with soft mutton and whole spices", 429, False, "Biryani", "mutton dum biryani.avif", True, 4.8, 35),
        ("Paneer Biryani", "Marinated paneer, fried onions and mint", 289, True, "Biryani", "paneer biryani.avif", False, 4.4, 26),
        ("Egg Biryani", "Spiced rice with boiled eggs and caramelised onion", 259, False, "Biryani", "egg biryani.avif", False, 4.3, 24),
        ("Prawns Biryani", "Coastal prawns tossed with basmati and curry leaf", 449, False, "Biryani", "prawns biryani.avif", False, 4.6, 32),
        ("Chicken 65 Biryani", "Biryani topped with fiery Chicken 65", 369, False, "Biryani", "chicken 65 biryani.avif", True, 4.7, 30),
        ("Butter Naan", "Pillowy naan brushed with butter", 49, True, "Breads", "butter naan.avif", False, 4.4, 8),
        ("Rumali Roti", "Paper-thin hand-spun roti", 29, True, "Breads", "rumali roti.avif", False, 4.2, 6),
        ("Chicken 65", "Crispy, spicy and unapologetically South Indian", 279, False, "Starters", "chicken 65.avif", True, 4.6, 16),
    ],
    "wok-and-roll": [
        ("Chicken Hakka Noodles", "Wok-tossed noodles with shredded chicken", 229, False, "Noodles", "chicken noodles.avif", True, 4.6, 16),
        ("Veg Hakka Noodles", "Classic street-style veg noodles", 189, True, "Noodles", "veg noodels.avif", True, 4.4, 15),
        ("Chicken Fried Rice", "Egg, spring onion and burnt garlic", 219, False, "Rice", "chiken fried rice.avif", True, 4.5, 16),
        ("Egg Fried Rice", "Comforting rice with scrambled egg", 179, True, "Rice", "egg fried rice.avif", False, 4.2, 14),
        ("Veg Manchurian", "Crisp veg balls in tangy Manchurian gravy", 199, True, "Starters", "veg manchurian.jpg_compressed", False, 4.3, 15),
        ("Chilli Paneer", "Paneer cubes tossed in chilli-garlic sauce", 239, True, "Starters", "chilli paneer.avif", True, 4.6, 15),
        ("Chicken Manchow Soup", "Hot and spicy soup with fried noodles", 149, False, "Soups", "chicken manchow soup.avif", False, 4.4, 10),
        ("Chicken Manchurian Roll", "Manchurian wrapped in a soft tortilla", 189, False, "Wraps", "chicken manchurian roll.avif", False, 4.3, 14),
    ],
    "shawarma-street": [
        ("Chicken Shawarma with Salad", "Juicy chicken, garlic sauce and fresh salad", 189, False, "Shawarma", "chicken shawarama with sald.avif", True, 4.7, 12),
        ("Special Chicken Shawarma", "Double chicken, extra garlic sauce", 229, False, "Shawarma", "spl chicken shawarama without sald.avif", True, 4.6, 12),
        ("Paneer Shawarma", "Tandoori paneer with mint mayo", 169, True, "Shawarma", "paneer shawarama.avif", False, 4.4, 12),
        ("Veg Shawarma", "Crispy veggies and tahini in pita", 139, True, "Shawarma", "veg shawarama.avif", False, 4.2, 10),
        ("Chicken Kebab Roll", "Smoky kebab, onion and chutney roll", 179, False, "Rolls", "chicken kebab roll.avif", True, 4.5, 12),
        ("Chicken Roll", "Street-style chicken roll with masala", 159, False, "Rolls", "chicken roll.avif", False, 4.3, 11),
        ("Egg Roll", "Flaky paratha with spiced egg filling", 119, True, "Rolls", "egg roll.avif", False, 4.1, 10),
        ("Spicy Chicken Wrap", "Fiery chicken wrap with crunchy slaw", 199, False, "Wraps", "spicy chicken wrap.avif", False, 4.4, 12),
    ],
    "mandi-house": [
        ("Chicken Juicy Mandi", "Slow-roasted chicken over fragrant mandi rice", 449, False, "Mandi", "chicken juicy mandi.avif", True, 4.9, 32),
        ("Chicken Fry Mandi", "Crisp-fried chicken with mandi rice", 429, False, "Mandi", "chicken fry mandi.avif", True, 4.8, 30),
        ("Chicken 65 Mandi", "Mandi rice topped with spicy Chicken 65", 399, False, "Mandi", "chicken 65 mandi.avif", False, 4.6, 30),
        ("Mutton Juicy Mandi", "Tender mutton, smoke-kissed rice", 549, False, "Mandi", "mutton jucy mandi.avif", True, 4.8, 38),
        ("Mutton Fry Mandi", "Fried mutton chunks with mandi rice", 529, False, "Mandi", "mutton fry mandi.avif", False, 4.7, 36),
        ("Fish Fry Mandi", "Coastal fried fish with mandi rice", 479, False, "Mandi", "fish fry mandi.avif", False, 4.5, 34),
        ("Paneer Mandi", "Charred paneer with aromatic rice", 349, True, "Mandi", "panner mandi.avif", False, 4.3, 28),
        ("Chicken Tandoori Mandi", "Tandoori chicken with mandi rice", 469, False, "Mandi", "chicken tandoori mandi.avif", True, 4.7, 34),
    ],
    "punjab-grill": [
        ("Butter Chicken", "Creamy tomato gravy with tandoori chicken", 349, False, "Curries", "butter chicken.avif", True, 4.9, 24),
        ("Punjabi Chicken", "Robust home-style chicken curry", 319, False, "Curries", "panjabi chicken.avif", True, 4.6, 24),
        ("Kaju Chicken", "Chicken in rich cashew gravy", 359, False, "Curries", "kaju chicken.avif", False, 4.5, 26),
        ("Paneer Butter Masala", "Silky tomato gravy with paneer cubes", 299, True, "Curries", "panner butter masala.avif", True, 4.7, 22),
        ("Kaju Paneer Butter Masala", "Cashew-rich gravy with soft paneer", 329, True, "Curries", "kaju paneer butter masala.jpg_compressed", False, 4.6, 24),
        ("Palak Paneer", "Creamy spinach with fresh paneer", 279, True, "Curries", "palak paneer.avif", False, 4.4, 20),
        ("Methi Chaman", "Fenugreek leaves with paneer in mild gravy", 289, True, "Curries", "methi chaman.avif", False, 4.3, 22),
        ("Chilli Mushroom", "Mushrooms tossed in Indo-Chinese chilli sauce", 249, True, "Starters", "chilli mushroom.avif", False, 4.3, 16),
        ("Butter Naan", "Soft tandoori naan with butter", 49, True, "Breads", "butter naan.avif", True, 4.5, 8),
        ("Tandoori Roti", "Whole wheat tandoori roti", 29, True, "Breads", "tandoori roti.avif", False, 4.2, 6),
    ],
    "cafe-irani": [
        ("Irani Tea", "Strong, milky, slow-brewed tea", 49, True, "Tea & Coffee", "irani tea.avif", True, 4.6, 6),
        ("Badam Tea", "Almond-infused classic chai", 69, True, "Tea & Coffee", "badam tea.avif", False, 4.4, 6),
        ("Dum Tea", "Slow-steeped, deeply aromatic chai", 59, True, "Tea & Coffee", "dum tea.avif", False, 4.3, 6),
        ("Ginger Tea", "Warming ginger brew", 49, True, "Tea & Coffee", "ginger tea.avif", False, 4.2, 6),
        ("Lemon Tea", "Light and refreshing black tea", 49, True, "Tea & Coffee", "lemon tea.avif", False, 4.1, 6),
        ("Veg Sandwich", "Crunchy veggies with mint chutney", 119, True, "Sandwiches", "veg sandwich.avif", True, 4.4, 10),
        ("Grilled Veg Sandwich", "Toasted sandwich with grilled vegetables", 149, True, "Sandwiches", "grilled veg sandwich.avif", True, 4.5, 12),
        ("Corn Sandwich", "Sweet corn and cheese filling", 139, True, "Sandwiches", "corn sandwich.jpg_compressed", False, 4.3, 10),
        ("Paneer Sandwich", "Spiced paneer and cheese toastie", 169, True, "Sandwiches", "paneer sandwich.jpg_compressed", False, 4.4, 12),
    ],
    "sweet-cravings": [
        ("Oreo Milkshake", "Thick cookies-and-cream shake", 179, True, "Shakes", "oreo milkshake.avif", True, 4.8, 8),
        ("Chocolate Milkshake", "Rich Belgian chocolate shake", 169, True, "Shakes", "chocolate milkshake.avif", True, 4.7, 8),
        ("Strawberry Milkshake", "Fresh strawberry blended with milk", 159, True, "Shakes", "strawberry milkshake.avif", False, 4.4, 8),
        ("Butterscotch Milkshake", "Caramel bits and butterscotch cream", 169, True, "Shakes", "butterscotch milkshake.avif", False, 4.5, 8),
        ("Vanilla Milkshake", "Classic vanilla bean shake", 139, True, "Shakes", "vanila milkshake.avif", False, 4.2, 7),
        ("Dry Fruit Milkshake", "Loaded with almonds, cashew and pistachio", 189, True, "Shakes", "dry fruit milkshake.avif", False, 4.5, 9),
        ("Rose Milkshake", "Fragrant rose and milk dessert shake", 159, True, "Shakes", "rose milkshake.avif", False, 4.3, 8),
        ("Apple Milkshake", "Sweet apple blended with chilled milk", 149, True, "Shakes", "apple milkshake.avif", False, 4.2, 8),
    ],
    "mocktail-bar": [
        ("Blue Lagoon Mocktail", "Blue curacao, lemon and soda", 159, True, "Mocktails", "blue lagoon mocktail.avif", True, 4.7, 7),
        ("Fresh Lime Mocktail", "Zesty lime, mint and soda", 129, True, "Mocktails", "fresh lime mocktail.avif", True, 4.5, 6),
        ("Kiwi Mocktail", "Kiwi crush, lime and crushed ice", 169, True, "Mocktails", "kiwi mocktail.avif", False, 4.4, 7),
        ("Mango Mocktail", "Summer mango with a citrus twist", 159, True, "Mocktails", "mango mocktail.avif", False, 4.5, 7),
        ("Orange Mocktail", "Fresh orange, soda and orange peel", 149, True, "Mocktails", "orange mocktail.avif", False, 4.3, 7),
        ("Strawberry Mocktail", "Berry crush with mint leaves", 159, True, "Mocktails", "straberry mocktail.avif", False, 4.2, 7),
        ("Watermelon Mocktail", "Cool watermelon with a hint of lime", 149, True, "Mocktails", "water melon mocktail.avif", False, 4.4, 7),
    ],
    "soup-corner": [
        ("Tomato Shorba", "Slow-roasted tomato and herb soup", 129, True, "Soups", "tommato soup.avif", True, 4.5, 10),
        ("Sweet Corn Soup", "Creamy corn soup with soft corn kernels", 139, True, "Soups", "sweet corn soup.png_compressed", True, 4.4, 10),
        ("Mushroom Soup", "Earthy mushroom velouté", 149, True, "Soups", "mushroom soup.avif", False, 4.3, 11),
        ("Chicken Soup", "Clear chicken broth with herbs", 149, False, "Soups", "chicken soup.avif", False, 4.4, 11),
        ("Veg Manchow Soup", "Spicy veg soup with crisp noodles", 139, True, "Soups", "veg manchow soup.avif", False, 4.2, 10),
        ("Veg Soup", "Garden vegetables in a light broth", 119, True, "Soups", "veg soup.avif", False, 4.1, 10),
        ("Grilled Veg Sandwich", "Toasted multigrain with grilled veg", 149, True, "Sides", "grilled veg sandwich.avif", False, 4.4, 10),
    ],
    "green-bowl": [
        ("Veg Biryani", "Fragrant rice with seasonal vegetables", 249, True, "Mains", "veg biryani.png_compressed", True, 4.4, 22),
        ("Veg Fried Rice", "Wok-fired rice with crunchy vegetables", 179, True, "Mains", "veg fried rice.avif", False, 4.2, 15),
        ("Veg Chowmein", "Street-style veg noodles", 179, True, "Mains", "veg chowmein.avif", False, 4.3, 15),
        ("Paneer 65", "Crisp paneer tossed in spicy masala", 239, True, "Starters", "panner 65.avif", True, 4.6, 14),
        ("Chilli Paneer", "Paneer in sweet-spicy chilli sauce", 239, True, "Starters", "chilli paneer.avif", True, 4.5, 15),
        ("Palak Paneer", "Spinach gravy with fresh paneer", 269, True, "Mains", "palak paneer.avif", False, 4.4, 20),
        ("Veg Sandwich", "Garden vegetables on toasted bread", 119, True, "Sides", "veg sandwich.avif", False, 4.2, 10),
        ("Fresh Lime Mocktail", "Cool lime and mint cooler", 129, True, "Drinks", "fresh lime mocktail.avif", False, 4.4, 6),
    ],
}

RESTAURANTS = [
    dict(slug="pizza-roma", name="Pizza Roma", cuisine="Italian, Pizza", area="Indiranagar",
         rating=4.6, rating_count=2140, delivery_min=28, price_for_two=600,
         image=img("margherita pizza.avif"), offer="50% OFF up to ₹150",
         accent="#FF5A1F", badges="Bestseller,Wood-fired", is_promo=True),
    dict(slug="burger-hub", name="Burger Hub", cuisine="American, Burgers", area="Koramangala",
         rating=4.5, rating_count=1780, delivery_min=24, price_for_two=450,
         image=img("chiken burger.avif"), offer="Buy 1 Get 1 on Burgers",
         accent="#E8590C", badges="Trending", is_promo=True),
    dict(slug="biryani-nawab", name="Biryani Nawab", cuisine="Mughlai, Biryani", area="Charminar",
         rating=4.8, rating_count=5210, delivery_min=35, price_for_two=500,
         image=img("chicken dum biryani.avif"), offer="Flat 20% OFF on ₹499+",
         accent="#B45309", badges="Top Rated,Legendary"),
    dict(slug="wok-and-roll", name="Wok & Roll", cuisine="Chinese, Asian", area="HSR Layout",
         rating=4.3, rating_count=980, delivery_min=30, price_for_two=400,
         image=img("chicken noodles.avif"), offer="Free delivery",
         accent="#DC2626", badges="Fast Delivery"),
    dict(slug="shawarma-street", name="Shawarma Street", cuisine="Lebanese, Wraps", area="MG Road",
         rating=4.4, rating_count=1320, delivery_min=22, price_for_two=300,
         image=img("chicken shawarama with sald.avif"), offer="20% OFF above ₹299",
         accent="#CA8A04", badges="Late Night"),
    dict(slug="mandi-house", name="Mandi House", cuisine="Arabian, Mandi", area="Jubilee Hills",
         rating=4.7, rating_count=2410, delivery_min=38, price_for_two=700,
         image=img("chicken juicy mandi.avif"), offer="Flat ₹100 OFF",
         accent="#92400E", badges="Family Feast"),
    dict(slug="punjab-grill", name="Punjab Grill", cuisine="North Indian, Curries", area="Sector 29",
         rating=4.6, rating_count=3110, delivery_min=32, price_for_two=550,
         image=img("butter chicken.avif"), offer="30% OFF up to ₹120",
         accent="#C2410C", badges="Bestseller"),
    dict(slug="cafe-irani", name="Cafe Irani", cuisine="Cafe, Sandwiches", area="Banjara Hills",
         rating=4.2, rating_count=760, delivery_min=18, price_for_two=250,
         image=img("irani tea.avif"), offer="Buy 1 Get 1 Tea",
         accent="#0F766E", badges="Quick Bites"),
    dict(slug="sweet-cravings", name="Sweet Cravings", cuisine="Desserts, Shakes", area="Whitefield",
         rating=4.5, rating_count=1450, delivery_min=20, price_for_two=300,
         image=img("oreo milkshake.avif"), offer="Flat 25% OFF",
         accent="#BE185D", badges="Sweet Tooth", is_promo=True),
    dict(slug="mocktail-bar", name="Mocktail Bar", cuisine="Beverages, Mocktails", area="Church Street",
         rating=4.3, rating_count=640, delivery_min=15, price_for_two=250,
         image=img("blue lagoon mocktail.avif"), offer="Free delivery",
         accent="#0284C7", badges="Chilled"),
    dict(slug="soup-corner", name="Soup Corner", cuisine="Soups, Comfort Food", area="Jayanagar",
         rating=4.1, rating_count=420, delivery_min=25, price_for_two=300,
         image=img("tommato soup.avif"), offer="20% OFF",
         accent="#7C2D12", badges="Comfort"),
    dict(slug="green-bowl", name="Green Bowl", cuisine="Healthy, Pure Veg", area="Electronic City",
         rating=4.4, rating_count=890, delivery_min=26, price_for_two=400,
         image=img("veg biryani.png_compressed"), offer="Flat 25% OFF on bowls",
         accent="#15803D", badges="Pure Veg,Healthy"),
]

DEMO_USER = dict(
    name="Aarav Sharma",
    email="demo@foodieexpress.com",
    password="foodie123",
    phone="+91 98765 43210",
    address="Flat 402, Sunrise Residency, MG Road, Bengaluru",
)


def seed_database() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(Restaurant.id).limit(1)):
            return

        for data in RESTAURANTS:
            restaurant = Restaurant(**data)
            db.add(restaurant)
            db.flush()
            for (name, desc, price, veg, category, image, popular, rating, prep) in MENUS[data["slug"]]:
                db.add(
                    Dish(
                        restaurant_id=restaurant.id,
                        name=name,
                        description=desc,
                        price=float(price),
                        veg=veg,
                        category=category,
                        image=img(image),
                        popular=popular,
                        rating=rating,
                        prep_min=prep,
                    )
                )

        if not db.scalar(select(User.id).filter_by(email=DEMO_USER["email"])):
            db.add(
                User(
                    name=DEMO_USER["name"],
                    email=DEMO_USER["email"],
                    password_hash=hash_password(DEMO_USER["password"]),
                    phone=DEMO_USER["phone"],
                    address=DEMO_USER["address"],
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("Seeded FoodieExpress database.")


DINEOUT_VENUES = [
    dict(slug="sky-lounge", name="Sky Lounge", cuisine="Continental, Rooftop", area="Indiranagar",
         rating=4.7, price_for_two=1400, image=img("margherita pizza.avif"),
         offer="Flat 25% OFF on food bill", ambiance="Rooftop · Live music", accent="#6d28d9"),
    dict(slug="the-biryani-court", name="The Biryani Court", cuisine="Mughlai, Biryani", area="Charminar",
         rating=4.8, price_for_two=1100, image=img("chicken dum biryani.avif"),
         offer="Flat 20% OFF + free dessert", ambiance="Royal dining hall", accent="#b45309"),
    dict(slug="olive-and-fire", name="Olive & Fire", cuisine="Italian, Wood-fired", area="Koramangala",
         rating=4.6, price_for_two=1600, image=img("tikka chicken pizza.avif"),
         offer="Complimentary mocktails", ambiance="Candle-lit bistro", accent="#be185d"),
    dict(slug="wok-garden", name="Wok Garden", cuisine="Pan-Asian, Sushi", area="HSR Layout",
         rating=4.5, price_for_two=1300, image=img("chicken noodles.avif"),
         offer="20% OFF on weekend brunch", ambiance="Zen garden", accent="#0f766e"),
    dict(slug="punjab-rasoi", name="Punjab Rasoi", cuisine="North Indian, Tandoor", area="Sector 29",
         rating=4.6, price_for_two=1200, image=img("butter chicken.avif"),
         offer="Flat ₹200 OFF on ₹1500+", ambiance="Dhaba courtyard", accent="#c2410c"),
    dict(slug="mirage-mandi", name="Mirage Mandi", cuisine="Arabian, Mandi", area="Jubilee Hills",
         rating=4.7, price_for_two=1500, image=img("chicken juicy mandi.avif"),
         offer="Buy 1 Get 1 on mocktails", ambiance="Desert-themed terrace", accent="#92400e"),
    dict(slug="the-green-terrace", name="The Green Terrace", cuisine="Healthy, Pure Veg", area="Whitefield",
         rating=4.4, price_for_two=900, image=img("veg biryani.png_compressed"),
         offer="Flat 25% OFF on salads", ambiance="Garden seating", accent="#15803d"),
    dict(slug="sweet-symphony", name="Sweet Symphony", cuisine="Desserts, Cafe", area="Church Street",
         rating=4.5, price_for_two=700, image=img("oreo milkshake.avif"),
         offer="Free hot chocolate", ambiance="Parisian cafe", accent="#a21caf"),
]


def seed_dineout() -> None:
    from app.models import DineoutVenue

    db = SessionLocal()
    try:
        if db.scalar(select(DineoutVenue.id).limit(1)):
            return
        for venue in DINEOUT_VENUES:
            db.add(DineoutVenue(**venue))
        db.commit()
    finally:
        db.close()
