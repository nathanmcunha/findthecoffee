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
        {"name": "Intelligentsia", "website": "https://www.intelligentsiacoffee.com", "location": "USA"},
        {"name": "Counter Culture", "website": "https://counterculturecoffee.com", "location": "USA"},
        {"name": "Ninety Plus", "website": "https://ninetypluscoffee.com", "location": "Panama"},
        {"name": "George Howell", "website": "https://www.georgehowellcoffee.com", "location": "USA"},
        {"name": "Onyx Coffee Lab", "website": "https://www.onyxcoffeelab.com", "location": "USA"},
    ]

    roaster_ids = {}
    for r in roasters_data:
        rid = roaster_repo.create(r["name"], r["website"], r["location"])
        roaster_ids[r["name"]] = rid
        print(f"🏭 Created Roaster: {r['name']} (ID: {rid})")

    # 2. Create Beans linked to Roasters
    beans_data = [
        # Five Roasters
        {"name": "Five Blend", "roaster": "Five Roasters", "roast": "Medium-Dark", "origin": "Brazil/Ethiopia"},
        {"name": "Cerrado Mineiro", "roaster": "Five Roasters", "roast": "Medium", "origin": "Brazil"},
        
        # Tocaya
        {"name": "Bourbon Amarelo", "roaster": "Tocaya", "roast": "Medium", "origin": "Brazil"},
        {"name": "Catuaí Vermelho", "roaster": "Tocaya", "roast": "Light", "origin": "Brazil"},
        {"name": "Mundo Novo", "roaster": "Tocaya", "roast": "Medium", "origin": "Brazil"},
        
        # Blue Bottle
        {"name": "Hayes Valley Espresso", "roaster": "Blue Bottle", "roast": "Medium", "origin": "Multi"},
        {"name": "Bella Donovan", "roaster": "Blue Bottle", "roast": "Medium-Dark", "origin": "Ethiopia/Guatemala"},
        {"name": "Three Africas", "roaster": "Blue Bottle", "roast": "Light-Medium", "origin": "Ethiopia/Kenya/Rwanda"},
        
        # Intelligentsia
        {"name": "Black Cat Espresso", "roaster": "Intelligentsia", "roast": "Medium-Dark", "origin": "Multi"},
        {"name": "Anacostia", "roaster": "Intelligentsia", "roast": "Medium", "origin": "Colombia"},
        {"name": "Hologram", "roaster": "Intelligentsia", "roast": "Medium", "origin": "Ethiopia"},
        
        # Counter Culture
        {"name": "Hologram Blend", "roaster": "Counter Culture", "roast": "Medium", "origin": "Ethiopia/Kenya"},
        {"name": "Big Trouble", "roaster": "Counter Culture", "roast": "Medium-Dark", "origin": "Guatemala/Colombia"},
        
        # Ninety Plus
        {"name": "Gesha", "roaster": "Ninety Plus", "roast": "Light", "origin": "Panama"},
        {"name": "Red Label", "roaster": "Ninety Plus", "roast": "Medium", "origin": "Panama"},
        
        # George Howell
        {"name": "Boquete Estate", "roaster": "George Howell", "roast": "Light-Medium", "origin": "Panama"},
        
        # Onyx Coffee Lab
        {"name": "Colombia La Esperanza", "roaster": "Onyx Coffee Lab", "roast": "Light", "origin": "Colombia"},
        {"name": "Ethiopia Worka Chelbessa", "roaster": "Onyx Coffee Lab", "roast": "Light", "origin": "Ethiopia"},
    ]

    bean_ids = {}
    for b in beans_data:
        bid = bean_repo.create(
            name=b["name"],
            roaster_id=roaster_ids[b["roaster"]],
            roast_level=b["roast"],
            origin=b["origin"]
        )
        bean_ids[b["name"]] = bid
        print(f"🫘 Created Bean: {b['name']} by {b['roaster']} (ID: {bid})")

    # 3. Create Cafes with geolocation and their Inventory
    cafes_data = [
        {
            "name": "Specialty Coffee House",
            "location": "São Paulo, SP",
            "address": "Rua Augusta, 1234 - Consolação, São Paulo - SP",
            "website": "https://specialtycoffeehouse.com.br",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "inventory": ["Bourbon Amarelo", "Five Blend"]
        },
        {
            "name": "The Minimalist Brew",
            "location": "Curitiba, PR",
            "address": "Rua XV de Novembro, 500 - Centro, Curitiba - PR",
            "website": "https://minimalistbrew.com.br",
            "latitude": -25.4284,
            "longitude": -49.2733,
            "inventory": ["Catuaí Vermelho", "Five Blend", "Hayes Valley Espresso"]
        },
        {
            "name": "Café Cultura",
            "location": "Rio de Janeiro, RJ",
            "address": "Av. Atlântica, 2000 - Copacabana, Rio de Janeiro - RJ",
            "website": "https://cafecultura.com.br",
            "latitude": -22.9068,
            "longitude": -43.1729,
            "inventory": ["Bourbon Amarelo", "Mundo Novo", "Black Cat Espresso"]
        },
        {
            "name": "Espresso Lab",
            "location": "Belo Horizonte, MG",
            "address": "Rua da Bahia, 1148 - Centro, Belo Horizonte - MG",
            "website": "https://espressolab.com.br",
            "latitude": -19.9167,
            "longitude": -43.9345,
            "inventory": ["Hayes Valley Espresso", "Bella Donovan", "Hologram"]
        },
        {
            "name": "Coffee & Co.",
            "location": "Porto Alegre, RS",
            "address": "Rua dos Andradas, 1000 - Centro Histórico, Porto Alegre - RS",
            "website": "https://coffeeandco.com.br",
            "latitude": -30.0346,
            "longitude": -51.2177,
            "inventory": ["Five Blend", "Cerrado Mineiro", "Big Trouble"]
        },
        {
            "name": "Brew Point",
            "location": "Brasília, DF",
            "address": "SCN Quadra 5 - Asa Norte, Brasília - DF",
            "website": "https://brewpoint.com.br",
            "latitude": -15.7801,
            "longitude": -47.9292,
            "inventory": ["Gesha", "Red Label", "Boquete Estate"]
        },
        {
            "name": "Third Wave Coffee",
            "location": "Florianópolis, SC",
            "address": "Rua Felipe Schmidt, 300 - Centro, Florianópolis - SC",
            "website": "https://thirdwavecoffee.com.br",
            "latitude": -27.5954,
            "longitude": -48.5480,
            "inventory": ["Colombia La Esperanza", "Ethiopia Worka Chelbessa", "Three Africas"]
        },
        {
            "name": "Origin Coffee Bar",
            "location": "Salvador, BA",
            "address": "Av. Sete de Setembro, 2000 - Vitória, Salvador - BA",
            "website": "https://origincoffeebar.com.br",
            "latitude": -13.0067,
            "longitude": -38.5108,
            "inventory": ["Anacostia", "Hologram Blend", "Catuaí Vermelho"]
        }
    ]

    for c in cafes_data:
        cid = cafe_repo.create(
            name=c["name"],
            location=c["location"],
            website=c["website"]
        )
        # Update with address and geolocation
        update_query = """
            UPDATE cafes 
            SET address = :address, latitude = :latitude, longitude = :longitude 
            WHERE id = :id
        """
        cafe_repo.db.execute(update_query, {
            "address": c["address"],
            "latitude": c["latitude"],
            "longitude": c["longitude"],
            "id": cid
        })
        print(f"☕ Created Cafe: {c['name']} (ID: {cid}) @ {c['location']}")

        for bean_name in c["inventory"]:
            cafe_repo.add_to_inventory(cid, bean_ids[bean_name])
            print(f"   📦 Linked {bean_name} to inventory")

    print("\n✨ Seeding complete!")
    print(f"\n📊 Summary:")
    print(f"   - {len(roasters_data)} Roasters")
    print(f"   - {len(beans_data)} Coffee Beans")
    print(f"   - {len(cafes_data)} Cafes")
    print(f"   - {sum(len(c['inventory']) for c in cafes_data)} Inventory Links")

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql+psycopg://user:password@localhost:5432/coffeedb"

    seed()
