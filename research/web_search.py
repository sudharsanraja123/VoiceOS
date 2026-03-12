from duckduckgo_search import DDGS


def search_web(query, max_results=5):

    results = []

    with DDGS() as ddgs:

        for r in ddgs.text(query, max_results=max_results):

            results.append({
                "title": r["title"],
                "link": r["href"]
            })

    return results