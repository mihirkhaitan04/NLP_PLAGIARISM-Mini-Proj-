import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

def search_web(query, max_results=5):
    """
    Search DuckDuckGo for a given query and return top results.
    Each result contains: title, url, snippet.
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
    except Exception as e:
        print(f"[Warn] Web search failed: {e}")
    return results


def scrape_page(url, timeout=5):
    """
    Fetch a URL and extract clean text content from the page.
    Returns the first ~2000 characters of meaningful text.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract text from paragraph tags for cleaner content
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)

        # Fallback to full body text if paragraphs are empty
        if len(text.strip()) < 50:
            text = soup.get_text(separator=" ", strip=True)

        # Return first 2000 chars to avoid processing massive pages
        return text[:2000]

    except Exception as e:
        print(f"[Warn] Failed to scrape {url}: {e}")
        return ""


def get_web_references(sentence, max_results=3):
    """
    For a given sentence, search the web and scrape top results.
    Returns a list of dicts: {url, title, text}
    """
    # Use the first 100 chars of the sentence as the search query
    query = sentence[:100]
    search_results = search_web(query, max_results=max_results)

    references = []
    for result in search_results:
        # First, use the search snippet as a quick reference
        snippet_text = result.get("snippet", "")

        # Then try to scrape the full page for deeper comparison
        page_text = scrape_page(result["url"])

        # Use whichever has more content
        ref_text = page_text if len(page_text) > len(snippet_text) else snippet_text

        if ref_text.strip():
            references.append({
                "url": result["url"],
                "title": result["title"],
                "text": ref_text
            })

    return references


# Quick test
if __name__ == "__main__":
    test_sentence = "Artificial intelligence has revolutionised the way we process information"
    refs = get_web_references(test_sentence)
    print(f"\nFound {len(refs)} web references:")
    for ref in refs:
        print(f"  - {ref['title']} ({ref['url']})")
        print(f"    Text preview: {ref['text'][:100]}...")
