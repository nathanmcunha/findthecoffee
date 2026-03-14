import random
from locust import HttpUser, task, between

class CoffeeUser(HttpUser):
    # Simulate a user waiting between 1 and 3 seconds between actions
    wait_time = between(1, 3)

    @task(10)
    def search_cafes(self):
        """High-frequency task: Searching across cafes, roasters, and beans."""
        queries = ["Specialty", "Five", "Brazil", "Tocaya", "Dark", "Hayes"]
        q = random.choice(queries)
        self.client.get(f"/api/cafes?q={q}", name="/api/cafes?q=[query]")

    @task(5)
    def list_all_cafes(self):
        """Medium-frequency task: Loading the main discovery page."""
        self.client.get("/api/cafes", name="/api/cafes")

    @task(3)
    def get_roasters(self):
        """Loading filters."""
        self.client.get("/api/roasters", name="/api/roasters")

    @task(1)
    def create_and_search(self):
        """Stress point: Create a cafe and immediately search for it (Triggers + Hybrid Fallback)."""
        cafe_name = f"Stress Cafe {random.randint(1000, 9999)}"
        
        # 1. Create the cafe
        with self.client.post("/api/cafes", json={"name": cafe_name, "location": "Stress City"}, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to create cafe: {response.status_code}")
        
        # 2. Immediate search for the new cafe (Tests zero-latency fallback)
        search_term = cafe_name.split()[-1] # The random number
        self.client.get(f"/api/cafes?q={search_term}", name="/api/cafes?q=[newly_created]")

    @task(2)
    def invalid_request(self):
        """Stress point: Hitting Pydantic validation with bad data."""
        # Missing 'name' field
        self.client.post("/api/cafes", json={"location": "Nowhere"}, name="/api/cafes [invalid]")
