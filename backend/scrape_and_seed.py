"""
Runs all three scrapers and seeds the database with scraped coffee data.

Usage:
    python scrape_and_seed.py

Requires DATABASE_URL to be set (via .env or environment).
"""

import json
import os
import subprocess

from dotenv import load_dotenv
from db.repository import CafeRepository, CoffeeBeanRepository, RoasterRepository

load_dotenv()


def run_scraper(script: str) -> list[dict]:
    """Run a scraper and return parsed beans from its JSON output."""
    print(f"\n{'='*60}")
    print(f"Running {script}...")
    print("=" * 60)
    result = subprocess.run(
        ["python", script],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"[ERROR] {script} failed:\n{result.stderr}")
        return []

    # Load the JSON file written by the scraper
    json_path = script.replace(".py", "_beans.json")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def clean_database():
    db = RoasterRepository().db
    print("\n🧹 Cleaning database...")
    for q in [
        "TRUNCATE TABLE cafe_inventory CASCADE",
        "TRUNCATE TABLE coffee_beans CASCADE",
        "TRUNCATE TABLE cafes CASCADE",
        "TRUNCATE TABLE roasters CASCADE",
    ]:
        db.execute(q)
    print("✅ Database cleaned.\n")


def seed():
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql+psycopg://user:password@localhost:5432/coffeedb"

    # 1. Clean
    clean_database()

    roaster_repo = RoasterRepository()
    bean_repo = CoffeeBeanRepository()

    # 2. Run all scrapers
    print("🌱 Running all scrapers...")
    tocaya_beans = run_scraper("scrape_tocaya.py")
    pandora_beans = run_scraper("scrape_pandora.py")
    pato_beans = run_scraper("scrape_pato.py")

    # 3. Create roasters
    roaster_map = {}  # name -> UUID
    roasters_data = [
        {"name": "Tocaya", "website": "https://tocaya.com.br/", "location": "Brazil"},
        {"name": "Pandora Coffee Roasters", "website": "https://pandoraroasters.com.br/", "location": "Brazil"},
        {"name": "Pato Rei", "website": "https://patoreisp.com.br/", "location": "Brazil"},
    ]
    for r in roasters_data:
        rid = roaster_repo.create(r["name"], r["website"], r["location"])
        roaster_map[r["name"]] = rid
        print(f"🏭 Created Roaster: {r['name']} (ID: {rid})")

    # 4. Insert beans per roaster
    all_beans = [
        (tocaya_beans, "Tocaya"),
        (pandora_beans, "Pandora Coffee Roasters"),
        (pato_beans, "Pato Rei"),
    ]

    for beans_list, roaster_name in all_beans:
        roaster_id = roaster_map[roaster_name]
        print(f"\n📦 Inserting {len(beans_list)} beans for {roaster_name}...")
        for b in beans_list:
            try:
                bid = bean_repo.create(
                    name=b["name"],
                    roaster_id=roaster_id,
                    roast_level=b.get("roast_level") or b.get("roast"),
                    origin=b.get("origin"),
                    variety=b.get("variety"),
                    processing=b.get("processing"),
                    altitude=b.get("altitude"),
                    producer=b.get("producer"),
                    farm=b.get("farm"),
                    region=b.get("region"),
                    tasting_notes=b.get("tasting_notes"),
                    acidity=b.get("acidity"),
                    sweetness=b.get("sweetness"),
                    body=b.get("body"),
                )
                notes = b.get("tasting_notes") or []
                print(
                    f"  🫘 {b['name']} | "
                    f"variety={b.get('variety', 'N/A')} | "
                    f"origin={b.get('origin', 'N/A')} | "
                    f"notes={notes[:3] if notes else 'none'}"
                )
            except Exception as e:
                print(f"  ⚠️  Failed to insert {b['name']}: {e}")

    print(f"\n✨ Seeding complete!")
    total = len(tocaya_beans) + len(pandora_beans) + len(pato_beans)
    print(f"   Roasters: {len(roasters_data)}")
    print(f"   Beans: {total} total")


if __name__ == "__main__":
    seed()