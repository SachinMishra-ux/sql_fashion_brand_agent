"""
setup_fashion_db.py
One-time script to create all fashion brand tables in Aiven MySQL
and seed them with rich sample data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection


# ──────────────────────────────────────────────────────────────
# DDL — Create Tables
# ──────────────────────────────────────────────────────────────
DDL = [
    # 1. Users / Customers
    """
    CREATE TABLE IF NOT EXISTS users (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        name          VARCHAR(120)    NOT NULL,
        email         VARCHAR(200)    UNIQUE NOT NULL,
        phone         VARCHAR(20),
        loyalty_tier  ENUM('Bronze','Silver','Gold','Platinum') DEFAULT 'Bronze',
        created_at    DATETIME        DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # 2. Products
    """
    CREATE TABLE IF NOT EXISTS products (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        name          VARCHAR(200)    NOT NULL,
        brand         VARCHAR(100)    NOT NULL,
        category      VARCHAR(80)     NOT NULL,
        subcategory   VARCHAR(80),
        price         DECIMAL(10,2)   NOT NULL,
        discount_pct  TINYINT         DEFAULT 0,
        stock         INT             DEFAULT 0,
        color         VARCHAR(50),
        size_range    VARCHAR(80),
        image_url     TEXT,
        description   TEXT,
        created_at    DATETIME        DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # 3. Catalogs (seasonal collections)
    """
    CREATE TABLE IF NOT EXISTS catalogs (
        id              INT AUTO_INCREMENT PRIMARY KEY,
        name            VARCHAR(200)  NOT NULL,
        season          ENUM('Spring','Summer','Autumn','Winter','All-Season') NOT NULL,
        year            YEAR          NOT NULL,
        description     TEXT,
        cover_image_url TEXT,
        launched_at     DATE
    )
    """,

    # 4. catalog_products (join table)
    """
    CREATE TABLE IF NOT EXISTS catalog_products (
        catalog_id  INT NOT NULL,
        product_id  INT NOT NULL,
        PRIMARY KEY (catalog_id, product_id),
        FOREIGN KEY (catalog_id) REFERENCES catalogs(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """,

    # 5. Orders
    """
    CREATE TABLE IF NOT EXISTS orders (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        user_id       INT           NOT NULL,
        product_id    INT           NOT NULL,
        quantity      TINYINT       NOT NULL DEFAULT 1,
        total_price   DECIMAL(10,2) NOT NULL,
        status        ENUM('Pending','Processing','Shipped','Delivered','Cancelled') DEFAULT 'Pending',
        order_date    DATETIME      DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id)    REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """,
]


# ──────────────────────────────────────────────────────────────
# Seed Data
# ──────────────────────────────────────────────────────────────

USERS = [
    ("Priya Sharma",     "priya.sharma@email.com",    "+91-9876543210", "Platinum"),
    ("Aisha Khan",       "aisha.khan@email.com",      "+91-9812345678", "Gold"),
    ("Riya Verma",       "riya.verma@email.com",      "+91-9898765432", "Gold"),
    ("Sneha Patel",      "sneha.patel@email.com",     "+91-9765432109", "Silver"),
    ("Neha Gupta",       "neha.gupta@email.com",      "+91-9654321098", "Silver"),
    ("Kavya Reddy",      "kavya.reddy@email.com",     "+91-9543210987", "Bronze"),
    ("Ananya Nair",      "ananya.nair@email.com",     "+91-9432109876", "Bronze"),
    ("Pooja Mehta",      "pooja.mehta@email.com",     "+91-9321098765", "Gold"),
    ("Divya Joshi",      "divya.joshi@email.com",     "+91-9210987654", "Silver"),
    ("Ishita Das",       "ishita.das@email.com",      "+91-9109876543", "Bronze"),
]

PRODUCTS = [
    # (name, brand, category, subcategory, price, discount_pct, stock, color, size_range, image_url, description)
    ("Silk Wrap Midi Dress",    "Luxé Studios",  "Dresses",   "Midi",    189.99, 10, 45, "Champagne",  "XS-XL",
     "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600",
     "Effortlessly elegant silk wrap dress with a fluid silhouette. Perfect for galas, brunches, and evening events."),

    ("Floral Maxi Gown",        "Bloom Couture", "Dresses",   "Maxi",    249.00,  5, 30, "Ivory/Rose", "XS-XXL",
     "https://images.unsplash.com/photo-1566479179817-b38b7ad5a389?w=600",
     "A dreamy floral maxi gown featuring hand-painted botanical prints on premium chiffon."),

    ("Tailored Blazer",         "Luxé Studios",  "Outerwear", "Blazer",  210.00, 15, 60, "Noir Black", "XS-XL",
     "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600",
     "Power-dressing redefined. Double-breasted tailored blazer with gold-tone button detailing."),

    ("Trench Coat Classic",     "Maison Forte",  "Outerwear", "Coat",    345.00,  0, 20, "Camel",      "S-XXL",
     "https://images.unsplash.com/photo-1548863227-3af567fc3b27?w=600",
     "Timeless double-breasted trench coat in premium water-resistant cotton gabardine."),

    ("Wide-Leg Linen Trousers", "EarthTone Co.", "Bottoms",   "Trousers",119.00, 20, 80, "Oat White",  "XS-XL",
     "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600",
     "Breathable wide-leg linen trousers for effortless summer styling."),

    ("High-Waist Denim Jeans",  "Denim8",        "Bottoms",   "Jeans",    99.00,  0, 120,"Indigo Blue","XS-XXL",
     "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600",
     "High-waist straight-cut denim with stretch comfort fabric. A wardrobe essential."),

    ("Cashmere Turtleneck",     "Maison Forte",  "Tops",      "Knitwear", 179.00,  0, 55, "Dusty Rose", "XS-XL",
     "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600",
     "100% Mongolian cashmere turtleneck. Unmatched softness and warmth for winter styling."),

    ("Off-Shoulder Linen Top",  "EarthTone Co.", "Tops",      "Blouse",   89.00, 10, 90, "Sage Green", "XS-XL",
     "https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?w=600",
     "Relaxed off-shoulder linen top with delicate ruffle neckline. Coastal chic essential."),

    ("Leather Tote Bag",        "Luxé Studios",  "Bags",      "Tote",    320.00,  0, 25, "Tan Brown",  None,
     "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600",
     "Structured leather tote with gold hardware. Spacious compartments for the modern woman."),

    ("Mini Chain Shoulder Bag", "Bloom Couture", "Bags",      "Shoulder", 195.00, 10, 40, "Pearl White",None,
     "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600",
     "Micro-quilted mini shoulder bag with a signature chain strap. A statement piece."),

    ("Block Heel Mules",        "Stride Luxe",   "Footwear",  "Mules",   159.00,  5, 35, "Nude Beige", "36-42",
     "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600",
     "Block heel mules in soft suede leather. Comfortable for all-day elegance."),

    ("Strappy Stiletto Heels",  "Stride Luxe",   "Footwear",  "Heels",   189.00,  0, 28, "Jet Black",  "35-42",
     "https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=600",
     "Sleek strappy stilettos with an adjustable ankle buckle. The ultimate evening shoe."),

    ("Pearl Drop Earrings",     "Lumino Jewels", "Jewelry",   "Earrings",  65.00,  0, 100,"Pearl/Gold", None,
     "https://images.unsplash.com/photo-1635767798638-3e25273a8236?w=600",
     "Freshwater pearl drop earrings set in 18k gold-plated sterling silver."),

    ("Gold Cuff Bracelet",      "Lumino Jewels", "Jewelry",   "Bracelet",  89.00,  0, 75, "Gold",       None,
     "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600",
     "Bold sculptural gold cuff bracelet. A power accessory for every occasion."),

    ("Silk Slip Skirt",         "Luxé Studios",  "Bottoms",   "Skirt",   145.00, 15, 50, "Blush Pink", "XS-XL",
     "https://images.unsplash.com/photo-1583496661160-fb5974ca3b00?w=600",
     "Bias-cut pure silk slip skirt that moves like water. Effortlessly sensual."),

    ("Oversized Linen Shirt",   "EarthTone Co.", "Tops",      "Shirt",    95.00, 20, 70, "Sky Blue",   "XS-XXL",
     "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600",
     "Relaxed oversized linen shirt. Style it tucked-in or as a beach cover-up."),
]

CATALOGS = [
    # (name, season, year, description, cover_image_url, launched_at)
    ("Luminary Spring 2025",    "Spring",  2025,
     "Where soft florals meet architectural structure. The Luminary collection celebrates femininity in full bloom.",
     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800", "2025-03-01"),

    ("Golden Hour Summer 2025", "Summer",  2025,
     "Sun-drenched hues, breathable linens, and coastal silhouettes define our Golden Hour summer edit.",
     "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800", "2025-06-01"),

    ("Noir Autumn 2024",        "Autumn",  2024,
     "A bold exploration of dark romanticism. Rich velvets, structured cuts, and deep jewel tones.",
     "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800", "2024-09-01"),

    ("Ivory Winter 2024",       "Winter",  2024,
     "Cashmere luxury meets minimalist pallor. The Ivory collection is pure Nordic elegance.",
     "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800", "2024-12-01"),
]

# Map catalog index → product indices (0-based)
CATALOG_PRODUCT_MAP = {
    0: [0, 1, 4, 7, 12],         # Spring 2025: dresses, linen, earrings
    1: [0, 4, 5, 7, 10, 15],     # Summer 2025: dresses, linens, mules
    2: [2, 3, 6, 9, 11, 13, 14], # Autumn 2024: blazer, coat, cashmere, bag, heels, bracelet
    3: [2, 3, 6, 8, 11, 13],     # Winter 2024: blazer, coat, cashmere, tote, heels, bracelet
}

ORDERS = [
    # (user_idx, product_idx, quantity, status)
    (0, 0, 1, "Delivered"),
    (0, 2, 1, "Delivered"),
    (1, 0, 1, "Shipped"),
    (1, 9, 1, "Delivered"),
    (2, 6, 2, "Processing"),
    (3, 4, 1, "Delivered"),
    (3, 3, 1, "Pending"),
    (4, 11, 1, "Delivered"),
    (5, 12, 2, "Delivered"),
    (6, 7, 1, "Processing"),
    (7, 1, 1, "Delivered"),
    (7, 8, 1, "Shipped"),
    (8, 5, 2, "Pending"),
    (9, 13, 1, "Delivered"),
    (0, 14, 1, "Delivered"),
    (1, 3, 1, "Cancelled"),
]


def seed(conn, cursor):
    print("Dropping foreign-key tables first...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for t in ["orders", "catalog_products", "catalogs", "products", "users"]:
        cursor.execute(f"TRUNCATE TABLE `{t}`;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()

    print("Inserting users...")
    cursor.executemany(
        "INSERT INTO users (name, email, phone, loyalty_tier) VALUES (%s,%s,%s,%s)",
        USERS
    )

    print("Inserting products...")
    cursor.executemany(
        """INSERT INTO products
           (name, brand, category, subcategory, price, discount_pct, stock, color, size_range, image_url, description)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        PRODUCTS
    )

    print("Inserting catalogs...")
    cursor.executemany(
        "INSERT INTO catalogs (name, season, year, description, cover_image_url, launched_at) VALUES (%s,%s,%s,%s,%s,%s)",
        CATALOGS
    )

    print("Linking catalog → products...")
    links = []
    for cat_idx, prod_indices in CATALOG_PRODUCT_MAP.items():
        for p_idx in prod_indices:
            links.append((cat_idx + 1, p_idx + 1))   # MySQL IDs are 1-based
    cursor.executemany(
        "INSERT IGNORE INTO catalog_products (catalog_id, product_id) VALUES (%s,%s)",
        links
    )

    print("Inserting orders...")
    order_rows = []
    for u_idx, p_idx, qty, status in ORDERS:
        price = PRODUCTS[p_idx][4]   # price column
        discount = PRODUCTS[p_idx][5]
        total = round(price * qty * (1 - discount / 100), 2)
        order_rows.append((u_idx + 1, p_idx + 1, qty, total, status))
    cursor.executemany(
        "INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES (%s,%s,%s,%s,%s)",
        order_rows
    )

    conn.commit()
    print("✅  All seed data committed successfully.")


def main():
    print("🔗  Connecting to Aiven MySQL...")
    conn = get_connection()
    cursor = conn.cursor()

    print("📐  Creating tables...")
    for stmt in DDL:
        cursor.execute(stmt)
    conn.commit()

    seed(conn, cursor)
    cursor.close()
    conn.close()
    print("🎉  Fashion brand database is ready!")


if __name__ == "__main__":
    main()
