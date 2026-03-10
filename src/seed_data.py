import os
from dotenv import load_dotenv
from src.db.repository import CafeRepository

# Load environment variables (ensure DATABASE_URL is set)
load_dotenv()

def seed():
    repo = CafeRepository()
    
    fake_cafes = [
        {"name": "Central Perk", "location": "Greenwich Village, NY"},
        {"name": "Luke's Diner", "location": "Stars Hollow, CT"},
        {"name": "Monk's Diner", "location": "Upper West Side, NY"},
        {"name": "The Roasted Bean", "location": "San Francisco, CA"},
        {"name": "Espresso Yourself", "location": "Seattle, WA"}
    ]
    
    print("🌱 Seeding database...")
    
    for cafe in fake_cafes:
        try:
            cafe_id = repo.create(cafe["name"], cafe["location"])
            print(f"✅ Created: {cafe['name']} (ID: {cafe_id})")
        except Exception as e:
            print(f"❌ Failed to create {cafe['name']}: {e}")

    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    # If running locally, you might need to override DATABASE_URL 
    # to point to localhost instead of the docker service name 'db'
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5432/coffeedb"
    
    seed()
