import re
import requests
from bs4 import BeautifulSoup

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_Armed_Forces_Hospitals_In_India"
API_URL = "http://127.0.0.1:8000/api/listings/bulk"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}

def clean(text: str | None) -> str | None:
    if not text:
        return None
    t = re.sub(r"\[\d+\]", "", text)  # remove citation markers like [1]
    t = re.sub(r"\s+", " ", t).strip()
    return t or None

def scrape_wikitable(url: str):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # Pick first wikitable (common for "List of ..." pages)
    table = soup.select_one("table.wikitable")
    if not table:
        raise RuntimeError("No wikitable found on the page. Page structure may differ.")

    # Read headers
    header_cells = table.select("tr th")
    headers = [clean(th.get_text(" ", strip=True)) for th in header_cells]

    # Read rows
    rows = []
    for tr in table.select("tr"):
        tds = tr.select("td")
        if not tds:
            continue
        row = [clean(td.get_text(" ", strip=True)) for td in tds]
        rows.append(row)

    return headers, rows

def map_rows_to_listings(headers, rows):
    """
    Try to infer columns. We'll handle variations by checking header keywords.
    """
    # Convert headers to lowercase for matching
    hlow = [h.lower() if h else "" for h in headers]

    def find_col(keywords):
        for i, h in enumerate(hlow):
            for k in keywords:
                if k in h:
                    return i
        return None

    name_col = find_col(["hospital", "name"])  # hospital name column
    location_col = find_col(["location", "place", "station", "city", "state"])

    listings = []
    for row in rows:
        if name_col is None or name_col >= len(row):
            continue
        name = row[name_col]
        if not name:
            continue

        location = None
        if location_col is not None and location_col < len(row):
            location = row[location_col]

        # If you want a fixed city (e.g. Hyderabad) you can set it here,
        # but for all-India list we store location in address.
        listings.append({
            "business_name": name[:255],
            "category": "Hospital",
            "city": None,
            "address": location,
            "phone": None,
            "source": "Wikipedia"
        })

    return listings

def bulk_insert(listings):
    resp = requests.post(API_URL, json={"listings": listings}, timeout=120)
    resp.raise_for_status()
    return resp.json()

def main():
    headers, rows = scrape_wikitable(WIKI_URL)
    listings = map_rows_to_listings(headers, rows)

    print("Parsed listings:", len(listings))
    if listings:
        print("Sample:", listings[0])

    if not listings:
        print("No listings parsed. We may need to adjust column detection.")
        return

    result = bulk_insert(listings)
    print("Inserted:", result)

if __name__ == "__main__":
    main()
