"""
Migration: Make category_id nullable in products and subcategories tables.

This allows products and subcategories to exist without a category (for reassignment).

Run with: python migrations/001_make_category_id_nullable.py
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


def get_db_path():
    """Extract SQLite database path from DATABASE_URL."""
    db_url = settings.DATABASE_URL
    if db_url.startswith('sqlite:///'):
        return db_url.replace('sqlite:///', '')
    return 'bot_database.db'


def migrate():
    """Run the migration to make category_id nullable."""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Run the bot first to create the database, then run this migration.")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # SQLite doesn't support ALTER COLUMN, so we need to recreate tables

        print("Starting migration: Make category_id nullable...")

        # --- Migrate subcategories table ---
        print("\n1. Migrating subcategories table...")

        # Check if migration needed
        cursor.execute("PRAGMA table_info(subcategories)")
        columns = cursor.fetchall()
        subcat_category_col = next((c for c in columns if c[1] == 'category_id'), None)

        if subcat_category_col and subcat_category_col[3] == 1:  # notnull = 1
            cursor.execute("""
                CREATE TABLE subcategories_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category_id INTEGER,
                    created_at DATETIME,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)
            cursor.execute("""
                INSERT INTO subcategories_new (id, name, category_id, created_at)
                SELECT id, name, category_id, created_at FROM subcategories
            """)
            cursor.execute("DROP TABLE subcategories")
            cursor.execute("ALTER TABLE subcategories_new RENAME TO subcategories")
            print("   ✓ subcategories.category_id is now nullable")
        else:
            print("   - subcategories.category_id already nullable, skipping")

        # --- Migrate products table ---
        print("\n2. Migrating products table...")

        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        prod_category_col = next((c for c in columns if c[1] == 'category_id'), None)

        if prod_category_col and prod_category_col[3] == 1:  # notnull = 1
            cursor.execute("""
                CREATE TABLE products_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price FLOAT NOT NULL,
                    stock_count INTEGER DEFAULT 0,
                    product_type VARCHAR(10) NOT NULL,
                    category_id INTEGER,
                    subcategory_id INTEGER,
                    image_path VARCHAR(500),
                    download_link VARCHAR(500),
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME,
                    FOREIGN KEY (category_id) REFERENCES categories(id),
                    FOREIGN KEY (subcategory_id) REFERENCES subcategories(id)
                )
            """)
            cursor.execute("""
                INSERT INTO products_new (id, name, description, price, stock_count, product_type,
                    category_id, subcategory_id, image_path, download_link, is_active, created_at)
                SELECT id, name, description, price, stock_count, product_type,
                    category_id, subcategory_id, image_path, download_link, is_active, created_at
                FROM products
            """)
            cursor.execute("DROP TABLE products")
            cursor.execute("ALTER TABLE products_new RENAME TO products")
            print("   ✓ products.category_id is now nullable")
        else:
            print("   - products.category_id already nullable, skipping")

        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
