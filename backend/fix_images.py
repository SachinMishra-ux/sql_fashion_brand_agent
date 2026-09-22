"""
fix_images.py
Updates all product image_urls in MySQL with verified working Unsplash photos.
Run once: uv run python fix_images.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection

# Verified working Unsplash photo IDs for each product (id → new url)
PRODUCT_IMAGES = {
    1:  "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=600&q=80&auto=format&fit=crop",  # Silk Wrap Midi Dress
    2:  "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&q=80&auto=format&fit=crop",  # Floral Maxi Gown
    3:  "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&q=80&auto=format&fit=crop",  # Tailored Blazer
    4:  "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=600&q=80&auto=format&fit=crop",  # Trench Coat
    5:  "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80&auto=format&fit=crop",  # Wide-Leg Trousers
    6:  "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80&auto=format&fit=crop",  # High-Waist Jeans
    7:  "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80&auto=format&fit=crop",  # Cashmere Turtleneck
    8:  "https://images.unsplash.com/photo-1485462537746-965f33f7f6a7?w=600&q=80&auto=format&fit=crop",  # Off-Shoulder Top
    9:  "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80&auto=format&fit=crop",  # Leather Tote Bag
    10: "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&q=80&auto=format&fit=crop",  # Mini Chain Shoulder Bag
    11: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&q=80&auto=format&fit=crop",  # Block Heel Mules
    12: "https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=600&q=80&auto=format&fit=crop",  # Strappy Stiletto Heels
    13: "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600&q=80&auto=format&fit=crop",  # Pearl Drop Earrings
    14: "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600&q=80&auto=format&fit=crop",  # Gold Cuff Bracelet
    15: "https://images.unsplash.com/photo-1583496661160-fb5974ca3b00?w=600&q=80&auto=format&fit=crop",  # Silk Slip Skirt
    16: "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80&auto=format&fit=crop",  # Oversized Linen Shirt
}

def main():
    print("🔗  Connecting...")
    conn = get_connection()
    cursor = conn.cursor()

    for prod_id, url in PRODUCT_IMAGES.items():
        cursor.execute(
            "UPDATE products SET image_url = %s WHERE id = %s",
            (url, prod_id)
        )
        print(f"  ✓  Product {prod_id:2d} → {url[:70]}…")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\n✅  Updated {len(PRODUCT_IMAGES)} product images successfully!")

if __name__ == "__main__":
    main()
