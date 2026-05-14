import re
import requests
from bs4 import BeautifulSoup

API_URL = "http://127.0.0.1:8000/api/listings/bulk"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}

def clean_phone(text: str | None):
    if not text:
        return None
    digits = re.sub(r"\D+", "", text)
    return digits if digits else None

def scrape_from_url(url: str, city: str, category: str, source: str):
    """
    Generic scraper template. You MUST adjust CSS selectors based on the website.
    """
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    # Try a few generic patterns (you can customize)
    cards = soup.select(".listing, .result, .card, .item")

    listings = []
    for card in cards:
        name_el = card.select_one(".name, .title, h2, h3, a")
        addr_el = card.select_one(".address, .addr, .location")
        phone_el = card.select_one(".phone, .contact, .mobile")

        name = name_el.get_text(" ", strip=True) if name_el else None
        address = addr_el.get_text(" ", strip=True) if addr_el else None
        phone = clean_phone(phone_el.get_text(" ", strip=True) if phone_el else None)

        if not name:
            continue

        listings.append({
            "business_name": name[:255],
            "category": category,
            "city": city,
            "address": address,
            "phone": phone,
            "source": source
        })

    return listings

def insert(listings):
    if not listings:
        print("No listings parsed. Probably need to update selectors for this website.")
        return
    resp = requests.post(API_URL, json={"listings": listings}, timeout=60)
    resp.raise_for_status()
    print("Inserted:", resp.json())

if __name__ == "__main__":
    # TODO: Replace this URL with a real directory/search results page you are allowed to scrape
    url = input("Paste the listings page URL to scrape: ").strip()
    city = input("City (for DB): ").strip() or "Unknown"
    category = input("Category (for DB): ").strip() or "Unknown"
    source = input("Source name (for DB, e.g. ExampleSite): ").strip() or "ExampleSite"

    data = scrape_from_url(url, city=city, category=category, source=source)
    print(f"Parsed {len(data)} listings")
    insert(data)
