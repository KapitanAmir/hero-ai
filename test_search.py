import requests

print("=" * 60)
print("        HERO AI - SEARCH ENGINE TEST")
print("=" * 60)

# --------------------------------------------------
# TEST 1 - DuckDuckGo Instant Answer
# --------------------------------------------------

print("\n[1] Testing DuckDuckGo...")

try:
    url = "https://api.duckduckgo.com/"
    params = {
        "q": "OpenAI",
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }

    r = requests.get(url, params=params, timeout=10)

    print("Status:", r.status_code)

    if r.ok:
        data = r.json()

        abstract = data.get("AbstractText", "")
        heading = data.get("Heading", "")

        print("Heading:", heading)
        print("Result:", abstract[:500] if abstract else "No direct answer")

        print("✅ DuckDuckGo: WORKING")
    else:
        print("❌ DuckDuckGo: FAILED")

except Exception as e:
    print("❌ DuckDuckGo ERROR:", e)


# --------------------------------------------------
# TEST 2 - Wikipedia
# --------------------------------------------------

print("\n[2] Testing Wikipedia...")

try:
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": "Artificial Intelligence",
        "format": "json",
        "utf8": 1,
    }

    r = requests.get(url, params=params, timeout=10)

    print("Status:", r.status_code)

    if r.ok:
        data = r.json()
        results = data.get("query", {}).get("search", [])

        if results:
            print("First result:", results[0]["title"])
            print("Snippet:", results[0]["snippet"][:300])
            print("✅ Wikipedia: WORKING")
        else:
            print("⚠️ Wikipedia responded but no results")

    else:
        print("❌ Wikipedia: FAILED")

except Exception as e:
    print("❌ Wikipedia ERROR:", e)


# --------------------------------------------------
# TEST 3 - Google connectivity
# --------------------------------------------------

print("\n[3] Testing Google connectivity...")

try:
    r = requests.get(
        "https://www.google.com/search",
        params={"q": "OpenAI"},
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=10,
    )

    print("Status:", r.status_code)

    if r.ok:
        print("✅ Google: ACCESSIBLE")
    else:
        print("❌ Google: FAILED")

except Exception as e:
    print("❌ Google ERROR:", e)


# --------------------------------------------------
# TEST 4 - Bing connectivity
# --------------------------------------------------

print("\n[4] Testing Bing connectivity...")

try:
    r = requests.get(
        "https://www.bing.com/search",
        params={"q": "OpenAI"},
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=10,
    )

    print("Status:", r.status_code)

    if r.ok:
        print("✅ Bing: ACCESSIBLE")
    else:
        print("❌ Bing: FAILED")

except Exception as e:
    print("❌ Bing ERROR:", e)


print("\n" + "=" * 60)
print("TEST FINISHED")
print("=" * 60)