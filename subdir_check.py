import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue

def find_broken_links_in_subsection(base_url, subsection_path):
    visited_urls = set()
    broken_links = {}

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

    def crawl_subsection(base_url, subsection_path):
        subsection_url = urljoin(base_url, subsection_path)
        q = Queue()
        q.put(subsection_url)

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
                print(f"Broken link on page: {url} (HTTP {response.status_code})")
                broken_links[url] = visited_urls.pop()
        except Exception as e:
            print(f"Error checking link {url}: {e}")

    crawl_subsection(base_url, subsection_path)

    if broken_links:
        print("\nBroken Links:")
        for link, referring_page in broken_links.items():
            print(f"Link: {link} (Found on page: {referring_page})")
    else:
        print("\nNo broken links found in the subsection.")

if __name__ == "__main__":
    base_url = "https://example.com"  # Replace with the base URL of the website
    subsection_path = "/subdirectory/"  # Replace with the path to the subsection
    find_broken_links_in_subsection(base_url, subsection_path)
