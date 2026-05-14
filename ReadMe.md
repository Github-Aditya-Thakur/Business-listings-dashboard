\# Business Listings Dashboard (React + FastAPI + MySQL)



\## Objective

A full‑stack, data‑driven dashboard that stores and visualizes business listings and shows aggregated reports:

\- City‑wise business count

\- Category‑wise business count

\- Source‑wise business count



This project uses:

\- \*\*Frontend:\*\* React (Vite) + Recharts

\- \*\*Backend:\*\* FastAPI (Python)

\- \*\*Database:\*\* MySQL



\---



\## Features

\- Bulk insert business listings into MySQL using a FastAPI endpoint

\- Dashboard APIs for aggregated counts:

&#x20; - City-wise count

&#x20; - Category-wise count

&#x20; - Source-wise count

\- React dashboard UI showing 3 charts (Bar / Pie)

\- Seed script to insert \*\*500+\*\* (currently 600) sample listings to make the project runnable without scraping blocks

\- Wikipedia multi-page scraper to insert \*\*1000+ real entries\*\* (idempotent; safe to rerun)



\---



\## Tech Stack

\- \*\*React.js\*\* (Vite)

\- \*\*FastAPI\*\* (Python)

\- \*\*MySQL\*\*

\- \*\*SQLAlchemy\*\* + \*\*PyMySQL\*\*

\- \*\*Recharts\*\* for charts



\---



\## Folder Structure

```

business-listings-dashboard/

&#x20; backend/

&#x20;   main.py

&#x20;   database.py

&#x20;   models.py

&#x20;   schemas.py

&#x20;   seed\_data.py

&#x20;   wiki\_multi\_scraper.py

&#x20;   .env

&#x20; frontend/

&#x20;   src/

&#x20;     App.jsx

&#x20;     Dashboard.jsx

&#x20;     api.js

&#x20; db\_dump.sql

&#x20; README.md

```



\---



\## Setup Instructions

pip install -r requirements.txt -- necessary

\### 1) Prerequisites

Install:

\- Node.js (LTS recommended)

\- Python 3.10+ (works with 3.12 too)

\- MySQL Community Server



Verify:

```bash

node -v

npm -v

python --version

mysql --version

```



\---



\## 2) Database Setup (MySQL)



Login:

```bash

mysql -u root -p

```



Run:

```sql

CREATE DATABASE IF NOT EXISTS business\_dashboard;

USE business\_dashboard;



CREATE TABLE IF NOT EXISTS listing\_master (

&#x20; id BIGINT AUTO\_INCREMENT PRIMARY KEY,

&#x20; business\_name VARCHAR(255) NOT NULL,

&#x20; category VARCHAR(255) NOT NULL DEFAULT '',

&#x20; city VARCHAR(100) NOT NULL DEFAULT '',

&#x20; address TEXT,

&#x20; phone VARCHAR(50),

&#x20; source VARCHAR(50) NOT NULL DEFAULT '',

&#x20; created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP

);



\-- Prevent duplicates (idempotent scraping / bulk inserts)

ALTER TABLE listing\_master

ADD CONSTRAINT uq\_listing\_dedupe

UNIQUE (business\_name, category, city, source);



CREATE INDEX idx\_city ON listing\_master(city);

CREATE INDEX idx\_category ON listing\_master(category);

CREATE INDEX idx\_source ON listing\_master(source);

```



> Note: If you already have an existing table with duplicates, you may need to remove duplicates before adding the UNIQUE constraint.



\---



\## 3) Backend Setup (FastAPI)

\### Create and activate venv

```bash

cd backend

python -m venv .venv

```



Activate:

\- Windows (PowerShell):

&#x20; ```bash

&#x20; .\\.venv\\Scripts\\Activate.ps1

&#x20; ```

\- macOS/Linux:

&#x20; ```bash

&#x20; source .venv/bin/activate

&#x20; ```



\### Install dependencies

```bash

pip install fastapi uvicorn sqlalchemy pymysql python-dotenv requests beautifulsoup4 pandas cryptography lxml

```



> Note: `cryptography` is required for MySQL auth methods like `caching\_sha2\_password`.



\### Configure environment variables

\*\*Copy .env.example to .env and update values. \*\*

Create `backend/.env`:

```env

DB\_HOST=localhost

DB\_PORT=3306

DB\_USER=root

DB\_PASSWORD=YOUR\_PASSWORD

DB\_NAME=business\_dashboard

```



\### Run backend

```bash

uvicorn main:app --reload --port 8000

```



Open:

\- Health: `http://127.0.0.1:8000/health`

\- Swagger Docs: `http://127.0.0.1:8000/docs`



\---



\## 4) Insert 500+ Listings (Seed Data)



From `backend/` (with backend running in another terminal):

```bash

python seed\_data.py

```



Expected output:

```json

{"inserted": 600}

```



Verify in MySQL:

```sql

USE business\_dashboard;

SELECT COUNT(\*) FROM listing\_master;

```



\---



\## 5) Wikipedia Scraping (1000+ real records)



This project includes a Wikipedia scraper that collects entities from multiple Wikipedia “List of …” pages (tables/lists) and inserts them using the bulk insert API.



From `backend/` (with backend running in another terminal):

```bash

python wiki\_multi\_scraper.py

```



Expected output (example):

```text

Total unique listings: 1075

Inserted: {'inserted': 1075, 'received': 1075}

```



Re-running the same script is safe (duplicates are ignored due to the UNIQUE constraint):

```text

Inserted: {'inserted': 0, 'received': 1075}

```



\---



\## 6) Frontend Setup (React)



```bash

cd frontend

npm install

npm run dev

```



Open:

\- `http://localhost:5173`



The dashboard displays:

\- City‑wise business count (Bar chart)

\- Category‑wise business count (Bar chart)

\- Source‑wise business count (Pie chart)



\---



\## API Endpoints



\### Bulk Insert

\*\*POST\*\* `/api/listings/bulk`



Request body:

```json

{

&#x20; "listings": \[

&#x20;   {

&#x20;     "business\_name": "Restaurant Business 1",

&#x20;     "category": "Restaurant",

&#x20;     "city": "Mumbai",

&#x20;     "address": "12, MG Road, Mumbai",

&#x20;     "phone": "9123456789",

&#x20;     "source": "SampleData"

&#x20;   }

&#x20; ]

}

```



Response:

```json

{ "inserted": 1, "received": 1 }

```



\### Dashboard Aggregations

\- \*\*GET\*\* `/api/dashboard/city-wise`

\- \*\*GET\*\* `/api/dashboard/category-wise`

\- \*\*GET\*\* `/api/dashboard/source-wise`



Response format:

```json

\[

&#x20; { "name": "Mumbai", "count": 120 },

&#x20; { "name": "Pune", "count": 90 }

]

```



\---



\## Scraping Approach (Notes)

Scraping can be blocked by many business directory websites and may have ToS restrictions.



This project supports two ingestion methods:

1\. \*\*Seed data\*\* for fully reproducible evaluation without external dependencies.

2\. \*\*Wikipedia scraping\*\* as a stable public source for collecting real-world lists into the same schema.



\---



\## Challenges Faced

\- \*\*MySQL authentication method (`caching\_sha2\_password`)\*\* required installing the `cryptography` package for PyMySQL.

\- \*\*Special characters in MySQL password (e.g., `@`)\*\* required URL-safe handling (encoding) in the DB connection string.

\- \*\*Scraping limitations\*\* on some platforms (bot detection / ToS). Used seed data for reproducibility, and Wikipedia lists for real scraped data.



\---



\## How to Generate Database Dump (Submission)

From the repo root (or anywhere):

```bash

mysqldump -u root -p business\_dashboard > db\_dump.sql

```



\---



\## Demo Video (What to Show)

1\. MySQL table and row count (500+)

2\. FastAPI `/docs` + dashboard endpoints

3\. React dashboard charts

4\. Seed + Wikipedia scraping approach explanation

5\. (Optional) Re-run `wiki\_multi\_scraper.py` to show idempotent inserts (0 new inserts)



\---



\## License

For internship assessment / educational use.

