import os
from dotenv import load_dotenv
from db.repository import CafeRepository, CoffeeBeanRepository, RoasterRepository

# Load environment variables (ensure DATABASE_URL is set)
load_dotenv()

def clean_database():
    """Wipes all tables to ensure a clean start for the new schema."""
    db = RoasterRepository().db
    print("🧹 Cleaning database...")
    queries = [
        "TRUNCATE TABLE cafe_inventory CASCADE",
        "TRUNCATE TABLE coffee_beans CASCADE",
        "TRUNCATE TABLE cafes CASCADE",
        "TRUNCATE TABLE roasters CASCADE",
    ]
    for q in queries:
        db.execute(q)
    print("✅ Database cleaned.")

def seed():
    clean_database()
    cafe_repo = CafeRepository()
    bean_repo = CoffeeBeanRepository()
    roaster_repo = RoasterRepository()

    print("🌱 Seeding database with Roaster-centric data...")

    # 1. Create Roasters
    roasters_data = [
        {"name": "Five Roasters", "website": "https://fiveroasters.com.br/", "location": "Brazil"},
        {"name": "Tocaya", "website": "https://tocaya.com.br/", "location": "Brazil"},
        {"name": "Blue Bottle", "website": "https://bluebottlecoffee.com", "location": "USA"},
    ]

    roaster_ids = {}
    for r in roasters_data:
        rid = roaster_repo.create(r["name"], r["website"], r["location"])
        roaster_ids[r["name"]] = rid
        print(f"🏭 Created Roaster: {r['name']} (ID: {rid})")

    # 2. Create Beans linked to Roasters with full technical details (ficha técnica)
    beans_data = [
        {
            "name": "Bourbon Amarelo",
            "roaster": "Tocaya",
            "roast": "Medium",
            "origin": "Brazil",
            "variety": "Bourbon Amarelo",
            "processing": "Natural",
            "altitude": 1100,
            "producer": "Fazenda Santa Isabel",
            "farm": "Bloco A",
            "region": "Sul de Minas, MG",
            "tasting_notes": ["Chocolate", "Caramelo", "Frutas vermelhas"],
            "acidity": 3,
            "sweetness": 4,
            "body": 4,
        },
        {
            "name": "Catuaí Vermelho",
            "roaster": "Tocaya",
            "roast": "Light",
            "origin": "Brazil",
            "variety": "Catuaí Vermelho",
            "processing": "Pulped Natural",
            "altitude": 1250,
            "producer": "Sítio Boa Vista",
            "farm": "Talhão 12",
            "region": "Cerrado Mineiro, MG",
            "tasting_notes": ["Mel", "Ameixa", "Chá preto"],
            "acidity": 4,
            "sweetness": 5,
            "body": 3,
        },
        {
            "name": "Five Blend",
            "roaster": "Five Roasters",
            "roast": "Medium-Dark",
            "origin": "Brazil/Ethiopia",
            "variety": "Blend",
            "processing": "Multiple",
            "altitude": 1000,
            "producer": "Five Roasters",
            "region": "Multi-origin",
            "tasting_notes": ["Nozes", "Chocolate amargo", "Especiarias"],
            "acidity": 2,
            "sweetness": 3,
            "body": 5,
        },
        {
            "name": "Hayes Valley Espresso",
            "roaster": "Blue Bottle",
            "roast": "Medium",
            "origin": "Multi",
            "variety": "Blend",
            "processing": "Washed",
            "altitude": 1200,
            "producer": "Blue Bottle",
            "region": "Multi-origin",
            "tasting_notes": ["Chocolate", "Citrus", "Floral"],
            "acidity": 3,
            "sweetness": 4,
            "body": 4,
        },
    ]

    bean_ids = {}
    for b in beans_data:
        bid = bean_repo.create(
            name=b["name"],
            roaster_id=roaster_ids[b["roaster"]],
            roast_level=b["roast"],
            origin=b["origin"],
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
        bean_ids[b["name"]] = bid
        print(f"🫘 Created Bean: {b['name']} by {b['roaster']} (ID: {bid})")

    # 3. Create Cafes and their Inventory
    cafes_data = [
        {
            "name": "Specialty Coffee House",
            "location": "São Paulo, SP",
            "inventory": ["Bourbon Amarelo", "Five Blend"]
        },
        {
            "name": "The Minimalist Brew",
            "location": "Curitiba, PR",
            "inventory": ["Catuaí Vermelho", "Five Blend", "Hayes Valley Espresso"]
        }
    ]

    for c in cafes_data:
        cid = cafe_repo.create(c["name"], c["location"])
        print(f"☕ Created Cafe: {c['name']} (ID: {cid})")

        for bean_name in c["inventory"]:
            cafe_repo.add_to_inventory(cid, bean_ids[bean_name])
            print(f"   📦 Linked {bean_name} to inventory")

    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql+psycopg://user:password@localhost:5432/coffeedb"

    seed()
