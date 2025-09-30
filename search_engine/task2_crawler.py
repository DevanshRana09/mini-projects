import argparse
import time
from collections import deque
from urllib.parse import urlparse
from task1_fetch_links import sanitize_url,fetch_html,extract_links


def get_root(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


# noinspection D
def crawl_seed(start_url, max_pages=10, delay=0.5):
    root = get_root(start_url)
    to_visit = deque([start_url])
    visited = set()
    links = []  # list of (from_url, to_url)

    while to_visit and len(visited) < max_pages:
        url = to_visit.popleft()
        if url in visited:
            continue

        html = fetch_html(url,time_out=10)
        if not html:
            # optionally record errors; skip this url
            visited.add(url)
            continue

        found = extract_links(html, url)
        for href in found:
            # scope check: only stay in same root
            if not href.startswith(root):
                continue
            links.append((url, href))
            # add to queue if not seen
            if href not in visited and href not in to_visit:
                to_visit.append(href)

        visited.add(url)
        time.sleep(delay)

    return visited, links

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Starting URL")
    parser.add_argument("--max", type=int, default=10, help="Max pages to crawl")
    args = parser.parse_args()

    # Use command-line argument if provided, otherwise ask via input()
    if args.start:
        start = args.start
        max_pages = args.max
    else:
        start = input("Enter starting URL [default: https://books.toscrape.com]: ").strip()
        if not start:
            start = "https://books.toscrape.com"
        max_pages_str=input("Enter max pages to crawl [default: 10]: ").strip()
        if not max_pages_str:
            max_pages = 10
        else:
            max_pages = int(max_pages_str)

    # Sanitize the start URL
    start = sanitize_url(start, start)

    visited, links = crawl_seed(start, max_pages=max_pages)

    print("Visited:", len(visited))
    print("Links:", len(links))
    print("Sample links (first 10):")
    for i, (f, t) in enumerate(links[:10], start=1):
        print(i, f, "->", t)


if __name__ == "__main__":
    main()

