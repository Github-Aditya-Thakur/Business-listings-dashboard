import random
import requests

API_URL = "http://127.0.0.1:8000/api/listings/bulk"

CITIES = ["Mumbai", "Pune", "Delhi", "Bengaluru"]
CATEGORIES = ["Restaurant", "Gym", "Salon", "Hospital"]
SOURCES = ["ScraperDemo"]  # this will appear in source-wise chart

def make_phone():
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))

def scrape_mock_data(n=50):
    """
    This function represents the 'scraping output'.
    In real scraping, you'd use requests + BeautifulSoup and return same structure.
    """
    data = []
    for i in range(1, n + 1):
        city = random.choice(CITIES)
        category = random.choice(CATEGORIES)
        data.append({
            "business_name": f"{category} Listing {i}",
            "category": category,
            "city": city,
            "address": f"{random.randint(1, 200)} Main Road, {city}",
            "phone": make_phone(),
            "source": SOURCES[0]
        })
    return data

def main():
    listings = scrape_mock_data(n=200)  # insert 200 more rows
    resp = requests.post(API_URL, json={"listings": listings}, timeout=60)
    resp.raise_for_status()
    print("Inserted:", resp.json())

if __name__ == "__main__":
    main()
