import base64
import logging
from typing import Dict, List
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup


logger = logging.getLogger("HeroAI.Search.Bing")

BING_URL = "https://www.bing.com/search"


# ============================================================
# BING URL CLEANER
# ============================================================

def clean_bing_url(url: str) -> str:
    """
    استخراج URL واقعی از لینک‌های redirect شده Bing.
    """

    if not url:
        return ""

    try:
        parsed = urlparse(url)

        # اگر لینک مستقیم بود
        if (
            parsed.netloc
            and "bing.com" not in parsed.netloc.lower()
        ):
            return url

        query = parse_qs(parsed.query)

        encoded = query.get("u", [None])[0]

        if not encoded:
            return url

        encoded = unquote(encoded)

        # Bing معمولاً مقدار u را به شکل a1 + Base64 می‌دهد
        if encoded.startswith("a1"):
            encoded = encoded[2:]

        # padding مربوط به Base64
        encoded += "=" * (
            (-len(encoded)) % 4
        )

        try:
            decoded = base64.b64decode(
                encoded
            ).decode(
                "utf-8",
                errors="ignore",
            )

            if decoded.startswith(
                (
                    "http://",
                    "https://",
                )
            ):
                return decoded

        except Exception:
            pass

    except Exception as e:

        logger.debug(
            "Could not clean Bing URL: %s",
            e,
        )

    return url


# ============================================================
# BING SEARCH
# ============================================================

async def search_bing(
    query: str,
    max_results: int = 5,
) -> List[Dict[str, str]]:
    """
    جستجوی وب از طریق Bing.

    خروجی:

    [
        {
            "title": "...",
            "url": "...",
            "snippet": "..."
        }
    ]
    """

    query = query.strip()

    if not query:
        return []

    max_results = max(
        1,
        min(max_results, 10),
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    params = {
        "q": query,
        "count": max_results,
        "setlang": "en-US",
    }

    try:

        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(
                BING_URL,
                params=params,
            )

            response.raise_for_status()

    except Exception as e:

        logger.warning(
            "Bing search failed: %s",
            e,
        )

        return []

    try:

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        results = []
        seen_urls = set()

        # ----------------------------------------------------
        # RESULT BLOCKS
        # ----------------------------------------------------

        for item in soup.select(
            "li.b_algo"
        ):

            if len(results) >= max_results:
                break

            title_element = item.select_one(
                "h2 a"
            )

            if not title_element:
                continue

            title = title_element.get_text(
                " ",
                strip=True,
            )

            raw_url = title_element.get(
                "href",
                "",
            )

            url = clean_bing_url(
                raw_url
            )

            snippet_element = (
                item.select_one(
                    ".b_caption p"
                )
                or item.select_one(
                    ".b_caption"
                )
            )

            snippet = ""

            if snippet_element:

                snippet = snippet_element.get_text(
                    " ",
                    strip=True,
                )

            if not title or not url:
                continue

            # ------------------------------------------------
            # REMOVE DUPLICATES
            # ------------------------------------------------

            normalized_url = url.rstrip(
                "/"
            ).lower()

            if normalized_url in seen_urls:
                continue

            seen_urls.add(
                normalized_url
            )

            results.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                }
            )

        logger.info(
            "Bing search returned %s results for: %s",
            len(results),
            query,
        )

        return results

    except Exception as e:

        logger.exception(
            "Error parsing Bing results: %s",
            e,
        )

        return []