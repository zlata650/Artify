from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring

START_URL = "https://www.sortiraparis.com/"
CONCERT_KEYWORDS = ["concert", "musique", "classique"]

def filter_by_keywords(links, keywords):
    """Return only links that contain at least one of the given keywords."""
    return [
        link for link in links
        if any(keyword.lower() in link.lower() for keyword in keywords)
    ]

def main():
    print(f"Fetching links from: {START_URL}")
    links = extract_links_from_url(START_URL)
    print(f"{len(links)} total links found.")

    concert_links = filter_by_keywords(links, CONCERT_KEYWORDS)
    print(f"{len(concert_links)} concert-related links found:\n")

    for link in concert_links:
        print(link)

if __name__ == "__main__":
    main()


