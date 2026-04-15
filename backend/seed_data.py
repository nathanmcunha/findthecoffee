import os
import json
import pathlib

from dotenv import load_dotenv
from db.repository import CafeRepository, CoffeeBeanRepository, RoasterRepository

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parent / "db" / "json_data_seed"


def clean_database():
    """Wipes all tables to ensure a clean start for the new schema."""
    db = RoasterRepository().db
    print("Cleaning database...")
    queries = [
        "TRUNCATE TABLE cafe_inventory CASCADE",
        "TRUNCATE TABLE coffee_beans CASCADE",
        "TRUNCATE TABLE cafes CASCADE",
        "TRUNCATE TABLE roasters CASCADE",
    ]
    for q in queries:
        db.execute(q)
    print("Database cleaned.")


def seed():
    clean_database()
    cafe_repo = CafeRepository()
    bean_repo = CoffeeBeanRepository()
    roaster_repo = RoasterRepository()

    print("Seeding database from JSON files...")

    # 1. Create roasters
    roasters_data = json.loads((DATA_DIR / "roasters.json").read_text(encoding="utf-8"))
    roaster_map = {}  # name -> UUID
    for r in roasters_data:
        rid = roaster_repo.create(r["name"], r["website"], r["location"])
        roaster_map[r["name"]] = rid
        print(f"Roaster: {r['name']} (ID: {rid})")

    # 2. Create beans from scraper JSON files
    bean_map = {}  # name (lowercase) -> UUID
    bean_files = [
        ("tocaya_beans.json", "Tocaya"),
        ("pandora_beans.json", "Pandora Coffee Roasters"),
        ("pato_beans.json", "Pato Rei"),
    ]
    total_beans = 0
    for filename, roaster_name in bean_files:
        beans_data = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        roaster_id = roaster_map[roaster_name]
        print(f"\n[{roaster_name}] {len(beans_data)} beans...")
        for b in beans_data:
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
                bean_map[b["name"].lower()] = bid
                notes = b.get("tasting_notes") or []
                print(
                    f"  {b['name']} | variety={b.get('variety', 'N/A')} | "
                    f"origin={b.get('origin', 'N/A')} | notes={notes[:3] if notes else 'none'}"
                )
                total_beans += 1
            except Exception as e:
                print(f"  Failed to insert {b['name']}: {e}")

    # 3. Create cafes and their inventory
    cafes_data = json.loads((DATA_DIR / "cafes.json").read_text(encoding="utf-8"))
    for c in cafes_data:
        cid = cafe_repo.create(c["name"], c["location"])
        print(f"\nCafe: {c['name']} (ID: {cid})")

        for bean_name in c.get("inventory", []):
            bean_id = bean_map.get(bean_name.lower())
            if bean_id:
                cafe_repo.add_to_inventory(cid, bean_id)
                print(f"  Linked '{bean_name}' to inventory")
            else:
                print(f"  WARNING: bean '{bean_name}' not found in database — skipping")

    print(f"\nSeeding complete!")
    print(f"  Roasters: {len(roasters_data)}")
    print(f"  Beans: {total_beans} total")
    print(f"  Cafes: {len(cafes_data)}")


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql+psycopg://user:password@localhost:5432/coffeedb"

    seed()
