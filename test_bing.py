import asyncio

from search.bing import search_bing


async def main():

    query = "OpenAI latest news"

    print("=" * 60)
    print("BING SEARCH TEST")
    print("=" * 60)

    results = await search_bing(
        query=query,
        max_results=5,
    )

    print()
    print(f"Results: {len(results)}")
    print()

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(f"[{index}] {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Snippet: {result['snippet']}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())