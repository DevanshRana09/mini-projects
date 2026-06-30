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
    - Resolves relative URLs correctly using urljoin before parsing.
    - Uses urllib.parse for robust component handling.
    - Adds case-insensitivity for extension checks.
    - Preserves query parameters.
    """
    if not href:
        return None

    # Resolve relative URLs first
    absolute_url = urljoin(base_url, href)

    # Parse using urllib for reliability
    parsed = urlparse(absolute_url)

    # Filter schemes (strict HTTP/HTTPS)
    if parsed.scheme not in ('http', 'https'):
        return None

    # Skip unwanted file types (case-insensitive)
    unwanted_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.zip', '.bmp')
    if parsed.path.lower().endswith(unwanted_extensions):
        return None

    # Normalize: Path trailing slash (only for paths > 1)
    # Reconstruct the path without the trailing slash
    path = parsed.path
    if len(path) > 1 and path.endswith('/'):
        path = path[:-1]

    # Reconstruct the URL properly
    # Using _replace to build the clean URL structure
    sanitized = parsed._replace(
        path=path,
        fragment=''  # Explicitly remove fragment
    )

    return sanitized.geturl()

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
