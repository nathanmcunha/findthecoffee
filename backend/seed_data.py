import os
from dotenv import load_dotenv
from db.repository import CafeRepository, CoffeeBeanRepository

# Load environment variables (ensure DATABASE_URL is set)
load_dotenv()

def seed():
    cafe_repo = CafeRepository()
    bean_repo = CoffeeBeanRepository()
    
    # Cafes with their coffee beans
    seed_data = [
        {
            "cafe": {"name": "Central Perk", "location": "Greenwich Village, NY"},
            "beans": [
                {"name": "House Blend", "roast_level": "Medium", "origin": "Colombia"},
                {"name": "Dark Roast Special", "roast_level": "Dark", "origin": "Brazil"},
            ]
        },
        {
            "cafe": {"name": "Luke's Diner", "location": "Stars Hollow, CT"},
            "beans": [
                {"name": "Morning Kick", "roast_level": "Dark", "origin": "Sumatra"},
            ]
        },
        {
            "cafe": {"name": "Blue Bottle", "location": "Oakland, CA"},
            "beans": [
                {"name": "Hayes Valley Espresso", "roast_level": "Medium", "origin": "Ethiopia/Uganda"},
                {"name": "Giant Steps", "roast_level": "Medium", "origin": "Latin America"},
                {"name": "Bella Donovan", "roast_level": "Medium-Dark", "origin": "Africa/Indonesia"},
            ]
        },
        {
            "cafe": {"name": "Stumptown Coffee", "location": "Portland, OR"},
            "beans": [
                {"name": "Hair Bender", "roast_level": "Medium", "origin": "Latin America/Africa"},
                {"name": "Holler Mountain", "roast_level": "Medium", "origin": "Colombia/Honduras"},
            ]
        },
        {
            "cafe": {"name": "Intelligentsia", "location": "Chicago, IL"},
            "beans": [
                {"name": "Black Cat Classic", "roast_level": "Medium", "origin": "Brazil/Colombia"},
                {"name": "House Espresso", "roast_level": "Light-Medium", "origin": "Ethiopia"},
            ]
        },
    ]
    
    print("🌱 Seeding database...")
    
    for entry in seed_data:
        cafe = entry["cafe"]
        try:
            cafe_id = cafe_repo.create(cafe["name"], cafe.get("location"))
            print(f"☕ Created cafe: {cafe['name']} (ID: {cafe_id})")
            
            for bean in entry.get("beans", []):
                bean_id = bean_repo.create(
                    name=bean["name"],
                    cafe_id=cafe_id,
                    roast_level=bean.get("roast_level"),
                    origin=bean.get("origin"),
                )
                print(f"   🫘 Added bean: {bean['name']} (ID: {bean_id})")
        except Exception as e:
            print(f"❌ Failed to create {cafe['name']}: {e}")

    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/coffeedb"
    
    seed()
