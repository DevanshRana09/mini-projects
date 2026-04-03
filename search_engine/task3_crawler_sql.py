import psycopg2
import time
from urllib.parse import urlparse
import requests

from task1_fetch_links import sanitize_url, extract_links,fetch_html

# ---- DB helper functions (implement these) ----
def init_db(conn):
    cur = conn.cursor()
    # Drop tables if they exist (for fresh start)

    # cur.execute("DROP TABLE IF EXISTS Links CASCADE")
    # cur.execute("DROP TABLE IF EXISTS Pages CASCADE")
    # cur.execute("DROP TABLE IF EXISTS Webs CASCADE")

    cur.execute("""CREATE TABLE IF NOT EXISTS Pages (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE,
        html BYTEA,
        error INTEGER,
        last_crawled TIMESTAMP,
        old_rank REAL,
        new_rank REAL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Links (
        from_id INTEGER,
        to_id INTEGER,
        UNIQUE(from_id, to_id),
        FOREIGN KEY(from_id) REFERENCES Pages(id),
        FOREIGN KEY(to_id) REFERENCES Pages(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)""")
    conn.commit()

def ensure_page(cur, url):
    """INSERT OR IGNORE page and return its id."""
    cur.execute("INSERT INTO Pages (url, html, new_rank) VALUES (%s, NULL, 1.0) ON CONFLICT (url) DO NOTHING", (url,))
    cur.execute("SELECT id FROM Pages WHERE url = %s LIMIT 1", (url,))
    row = cur.fetchone()
    return row[0]

def get_page_to_fetch(cur):
    """Return (id, url) for a page that needs HTML (html IS NULL and error IS NULL)."""
    cur.execute("SELECT id, url FROM Pages WHERE html IS NULL AND error IS NULL ORDER BY RANDOM() LIMIT 1")
    return cur.fetchone()  # returns None if empty

def record_page_html(cur, conn, url, html_bytes):
    """Store HTML and clear error."""
    cur.execute("UPDATE Pages SET html=%s, last_crawled=NOW(), error=NULL WHERE url=%s", (html_bytes, url))
    conn.commit()

def record_error(cur, conn, url, err_code=-1):
    cur.execute("UPDATE Pages SET error=%s WHERE url=%s", (err_code, url))
    conn.commit()


def record_link_if_html(cur, from_id, to_url):
    """Insert link only if to_url is HTML."""
    try:
        response = requests.head(to_url, allow_redirects=True, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return None
    except requests.RequestException:
        return None

    # Insert page if not exists
    cur.execute("INSERT INTO Pages (url, html, new_rank) VALUES (%s, NULL, 1.0) ON CONFLICT (url) DO NOTHING", (to_url,))
    cur.execute("SELECT id FROM Pages WHERE url=%s LIMIT 1", (to_url,))
    row = cur.fetchone()
    if not row:
        return None
    to_id = row[0]

    # Insert link relation
    cur.execute("INSERT INTO Links (from_id, to_id) VALUES (%s, %s) ON CONFLICT (from_id, to_id) DO NOTHING", (from_id, to_id))
    return to_id

# ---- crawler loop (DB-driven) ----
def get_root(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def db_crawl(start_url, db_host, db_user, db_password, db_name, max_pages=10, delay=0.5):
    conn = psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cur = conn.cursor()
    init_db(conn)

    # seed start_url if DB empty
    cur.execute("SELECT COUNT(*) FROM Pages")
    if cur.fetchone()[0] == 0:
        root = get_root(start_url)
        cur.execute("INSERT INTO Webs (url) VALUES (%s) ON CONFLICT (url) DO NOTHING", (root,))
        ensure_page(cur, start_url)
        conn.commit()

    pages_fetched = 0
    while pages_fetched < max_pages:
        row = get_page_to_fetch(cur)
        if not row:
            print("No more pages to fetch (html IS NULL and error IS NULL).")
            break
        from_id, url = row
        print("Fetching:", from_id, url)

        html = fetch_html(url, time_out=10)
        if not html:
            record_error(cur, conn, url, -1)
            pages_fetched += 1
            time.sleep(delay)
            continue

        # store html
        record_page_html(cur, conn, url, html.encode("utf-8"))
        pages_fetched += 1

        # extract links
        cur.execute("SELECT url FROM Webs")
        root_list = [r[0] for r in cur.fetchall()]
        found = extract_links(html, url)
        for href in found:
            # scope check
            if any(href.startswith(root) for root in root_list):
                record_link_if_html(cur, from_id, href)

        time.sleep(delay)

    conn.close()


# ---- run as script ----
if __name__ == "__main__":
    start = input("Enter starting URL [default: https://books.toscrape.com]: ").strip()
    if not start:
        start = "https://books.toscrape.com"
    start = sanitize_url(start, start)

    max_pages_str = input("Enter max pages to crawl [default: 10]: ").strip()
    if not max_pages_str:
        max_pages = 10
    else:
        max_pages = int(max_pages_str)

    # PostgreSQL connection parameters
    db_host = input("Enter PostgreSQL host [default: localhost]: ").strip() or "localhost"
    db_user = input("Enter PostgreSQL user [default: postgres]: ").strip() or "postgres"
    db_password = input("Enter PostgreSQL password [default: Dragon@009]: ").strip() or "Dragon@009"
    db_name = input("Enter PostgreSQL database name [default: spider_db]: ").strip() or "spider_db"

    db_crawl(start, db_host=db_host, db_user=db_user, db_password=db_password, db_name=db_name, max_pages=max_pages, delay=0.5)


