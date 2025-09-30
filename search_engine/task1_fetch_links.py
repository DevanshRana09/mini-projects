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

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'lxml')
    links = set()
    for tag in soup('a'):
        href = tag.get('href')
        if not href:
            continue
        href = urljoin(base_url, href)  # resolve relative
        href = href.split('#', 1)[0]    # remove fragments

        # Skip non-http(s)
        if urlparse(href).scheme not in ('http', 'https'):
            continue
        # Skip images
        if href.endswith(('.png', '.jpg', '.gif')):
            continue
        # Normalize trailing slash
        if href.endswith('/'):
            href = href[:-1]

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
