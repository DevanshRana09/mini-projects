import sys
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


def fetch_html(url, time_out=10):
    try:
        source = requests.get(url,timeout=time_out)
    except requests.exceptions.RequestException as e:
        print("Error on page: ",e)
        return None
    else:
        return source.text

def sanitize_url(href, base_url):
    """
    Clean and normalize a URL:
    - Resolve relative URLs to absolute
    - Remove fragments (#...)
    - Remove trailing slash
    - Skip unwanted schemes and file types
    """
    if not href:
        return None

    # Skip non-HTTP(s) links (like mailto:, javascript:)
    up = urlparse(href)
    if up.scheme not in ('http', 'https', ''):
        return None

    # Resolve relative URLs
    if len(up.scheme) < 1:
        href = urljoin(base_url, href)

    # Remove fragment
    href = href.split('#', 1)[0]

    # Skip images and binary files
    if href.endswith(('.png', '.jpg', '.gif', '.svg', '.pdf', '.zip')):
        return None

    # Normalize trailing slash
    if href.endswith('/'):
        href = href[:-1]

    # Ensure it's not empty after cleaning
    if len(href) < 1:
        return None

    return href

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()

    for tag in soup('a'):
        href = tag.get('href')
        href=sanitize_url(href, base_url)

        if href:
            links.add(href)

    return links


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        return

    html = fetch_html(url)
    if not html:
        print("Failed to fetch page.")
        return

    links = extract_links(html,url)
    print(f"Found {len(links)} unique links:")
    for link in sorted(links):
        print(link)

if __name__ == "__main__":
    main()
