import random
import requests

API_URL = "http://127.0.0.1:8000/api/listings/bulk"

CITIES = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]
CATEGORIES = ["Restaurant", "Gym", "Salon", "Hospital", "Pharmacy", "Hotel", "Cafe", "Coaching Center"]
SOURCES = ["SampleData", "Justdial", "Sulekha", "Google"]

STREETS = ["MG Road", "Link Road", "Station Road", "Ring Road", "Park Street", "Nehru Nagar", "Main Market"]

def make_phone():
    # Indian-like 10 digit mobile numbers (just for sample)
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))

def generate_listing(i: int):
    city = random.choice(CITIES)
    category = random.choice(CATEGORIES)
    source = random.choice(SOURCES)
    address = f"{random.randint(1, 250)}, {random.choice(STREETS)}, {city}"
    return {
        "business_name": f"{category} Business {i}",
        "category": category,
        "city": city,
        "address": address,
        "phone": make_phone(),
        "source": source
    }

def main():
    listings = [generate_listing(i) for i in range(1, 601)]  # 600 rows
    resp = requests.post(API_URL, json={"listings": listings}, timeout=60)
    resp.raise_for_status()
    print("Seed result:", resp.json())

if __name__ == "__main__":
    main()
