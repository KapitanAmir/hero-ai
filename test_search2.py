import requests
from bs4 import BeautifulSoup


def test_bing(query):
    print("\n" + "=" * 60)
    print("BING SEARCH")
    print("=" * 60)

    try:
        r = requests.get(
            "https://www.bing.com/search",
            params={"q": query},
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15,
        )

        print("Status:", r.status_code)

        if r.status_code != 200:
            print("❌ Bing failed")
            return

        soup = BeautifulSoup(r.text, "html.parser")

        results = soup.select("li.b_algo")

        if not results:
            print("⚠️ No results found")
            return

        for i, result in enumerate(results[:5], 1):
            title_tag = result.select_one("h2 a")

            if not title_tag:
                continue

            title = title_tag.get_text(" ", strip=True)
            link = title_tag.get("href", "")

            snippet_tag = result.select_one(".b_caption p")

            snippet = (
                snippet_tag.get_text(" ", strip=True)
                if snippet_tag
                else ""
            )

            print(f"\n[{i}] {title}")
            print("URL:", link)
            print("TEXT:", snippet[:400])

        print("\n✅ Bing search extraction works")

    except Exception as e:
        print("❌ Bing ERROR:", repr(e))


def test_duckduckgo(query):
    print("\n" + "=" * 60)
    print("DUCKDUCKGO SEARCH")
    print("=" * 60)

    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15,
        )

        print("Status:", r.status_code)

        if r.status_code != 200:
            print("❌ DuckDuckGo failed")
            return

        soup = BeautifulSoup(r.text, "html.parser")

        results = soup.select(".result")

        if not results:
            print("⚠️ No results found")
            return

        for i, result in enumerate(results[:5], 1):
            title_tag = result.select_one(".result__a")

            if not title_tag:
                continue

            title = title_tag.get_text(" ", strip=True)
            link = title_tag.get("href", "")

            snippet_tag = result.select_one(".result__snippet")

            snippet = (
                snippet_tag.get_text(" ", strip=True)
                if snippet_tag
                else ""
            )

            print(f"\n[{i}] {title}")
            print("URL:", link)
            print("TEXT:", snippet[:400])

        print("\n✅ DuckDuckGo search extraction works")

    except Exception as e:
        print("❌ DuckDuckGo ERROR:", repr(e))


if __name__ == "__main__":

    QUERY = "latest artificial intelligence news"

    print("=" * 60)
    print("       HERO AI - REAL SEARCH TEST")
    print("=" * 60)

    test_bing(QUERY)
    test_duckduckgo(QUERY)

    print("\n" + "=" * 60)
    print("TEST FINISHED")
    print("=" * 60)