import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue

def find_broken_links(base_url):
    visited_urls = set()
    broken_links = []

    def is_absolute(url):
        return bool(url.startswith("http") or url.startswith("//"))

    def make_absolute(url, base):
        if is_absolute(url):
            return url
        return urljoin(base, url)

    def get_links(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            links = [a.get("href") for a in soup.find_all("a", href=True)]
            return [make_absolute(link, url) for link in links]
        except Exception as e:
            print(f"Error fetching links from {url}: {e}")
            return []

    def crawl_website(base_url):
        q = Queue()
        q.put(base_url)

        while not q.empty():
            current_url = q.get()

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            print(f"Crawling: {current_url}")

            links = get_links(current_url)

            for link in links:
                if link not in visited_urls:
                    q.put(link)

            check_links(current_url)

    def check_links(url):
        try:
            response = requests.head(url, allow_redirects=True)
            if response.status_code >= 400:
                print(f"Broken link: {url} (HTTP {response.status_code})")
                broken_links.append(url)
        except Exception as e:
            print(f"Error checking link {url}: {e}")

    crawl_website(base_url)

    if broken_links:
        print("\nBroken Links:")
        for link in broken_links:
            print(link)
    else:
        print("\nNo broken links found on the website.")

if __name__ == "__main__":
    base_url = "https://example.com"  # Replace with the website you want to check
    find_broken_links(base_url)
