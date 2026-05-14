import re
import time
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup

API_URL = "http://127.0.0.1:8000/api/listings/bulk"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}

# Your URLs + chosen categories (you can edit these anytime)
TARGETS = [
    ("https://en.wikipedia.org/wiki/List_of_hospitals_in_India", "Hospital", "India"),
    ("https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_Hyderabad", "Building", "Hyderabad"),
    ("https://en.wikipedia.org/wiki/List_of_Hyderabad_Metro_stations", "Metro Station", "Hyderabad"),
    ("https://en.wikipedia.org/wiki/List_of_movie_theater_chains", "Theater Chain", None),
    ("https://en.wikipedia.org/wiki/List_of_highest-grossing_films", "Film", None),
    ("https://en.wikipedia.org/wiki/List_of_highest-grossing_R-rated_films", "Film", None),
    ("https://en.wikipedia.org/wiki/List_of_video_games_listed_among_the_best", "Video Game", None),
    ("https://en.wikipedia.org/wiki/List_of_Disney_Channel_original_films", "Film", None),
]

def clean(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    t = re.sub(r"\[\d+\]", "", text)          # remove [1], [2]
    t = re.sub(r"\s+", " ", t).strip()
    return t or None

def is_junk_name(name: str) -> bool:
    bad = {
        "notes", "references", "see also", "external links", "further reading",
        "next page", "previous page"
    }
    return name.strip().lower() in bad

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def infer_name_col(headers: List[str]) -> Optional[int]:
    """
    Try to find a column likely to contain the entity name.
    """
    h = [x.lower() for x in headers]
    keywords = ["name", "hospital", "station", "building", "film", "game", "title", "chain"]
    for i, col in enumerate(h):
        if any(k in col for k in keywords):
            return i
    return 0 if headers else None

def infer_location_col(headers: List[str]) -> Optional[int]:
    h = [x.lower() for x in headers]
    keywords = ["location", "city", "place", "area", "state", "country"]
    for i, col in enumerate(h):
        if any(k in col for k in keywords):
            return i
    return None

def parse_wikitables(soup: BeautifulSoup) -> List[Tuple[List[str], List[List[str]]]]:
    tables = []
    for table in soup.select("table.wikitable"):
        # headers can be in first row th's
        header_row = table.select_one("tr")
        headers = []
        if header_row:
            headers = [clean(th.get_text(" ", strip=True)) or "" for th in header_row.select("th")]
        rows = []
        for tr in table.select("tr"):
            tds = tr.select("td")
            if not tds:
                continue
            rows.append([clean(td.get_text(" ", strip=True)) or "" for td in tds])
        if rows:
            tables.append((headers, rows))
    return tables

def extract_from_tables(url: str, category: str, city: Optional[str]) -> List[Dict]:
    html = fetch(url)
    soup = BeautifulSoup(html, "lxml")

    tables = parse_wikitables(soup)
    listings: List[Dict] = []

    for headers, rows in tables:
        name_col = infer_name_col(headers)
        loc_col = infer_location_col(headers)

        for row in rows:
            if name_col is None or name_col >= len(row):
                continue
            name = clean(row[name_col])
            if not name or is_junk_name(name):
                continue

            address = None
            if loc_col is not None and loc_col < len(row):
                address = clean(row[loc_col])

            listings.append({
                "business_name": name[:255],
                "category": category,
                "city": city,
                "address": address,
                "phone": None,
                "source": "Wikipedia"
            })

    return listings

def extract_from_lists(url: str, category: str, city: Optional[str], limit: int = 200) -> List[Dict]:
    """
    Fallback when no wikitables exist or they are hard to parse:
    grabs <li> items from the main content.
    """
    html = fetch(url)
    soup = BeautifulSoup(html, "lxml")

    content = soup.select_one("#mw-content-text")
    if not content:
        return []

    items = []
    for li in content.select("ul li"):
        txt = clean(li.get_text(" ", strip=True))
        if not txt or is_junk_name(txt):
            continue
        # avoid very long paragraph-like list items
        if len(txt) > 120:
            continue
        items.append(txt)
        if len(items) >= limit:
            break

    return [
        {
            "business_name": name[:255],
            "category": category,
            "city": city,
            "address": None,
            "phone": None,
            "source": "Wikipedia"
        }
        for name in items
    ]

def bulk_insert(listings: List[Dict]) -> Dict:
    resp = requests.post(API_URL, json={"listings": listings}, timeout=180)
    resp.raise_for_status()
    return resp.json()

def dedupe(listings: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for x in listings:
        key = (x["business_name"].strip().lower(), (x.get("category") or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out

def main():
    all_listings: List[Dict] = []

    for url, category, city in TARGETS:
        print(f"\nScraping: {url}")
        try:
            rows = extract_from_tables(url, category=category, city=city)
            if not rows:
                print("  No table rows found, trying list fallback...")
                rows = extract_from_lists(url, category=category, city=city)

            rows = dedupe(rows)
            print(f"  Parsed: {len(rows)}")
            if rows:
                print("  Sample:", rows[0])

            all_listings.extend(rows)
            time.sleep(1)  # be polite to Wikipedia
        except Exception as e:
            print("  Failed:", repr(e))

    all_listings = dedupe(all_listings)
    print("\nTotal unique listings:", len(all_listings))

    if not all_listings:
        print("Nothing to insert.")
        return

    result = bulk_insert(all_listings)
    print("Inserted:", result)

if __name__ == "__main__":
    main()
