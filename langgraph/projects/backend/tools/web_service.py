from langchain_core.tools import tool
from ddgs import DDGS


# Sites to filter out from results
BLOCKED_SITES = [
    "roleplay", "rubii", "perchance", "character.ai",
    "reddit.com", "quora.com", "pinterest", "youtube"
]




@tool
def web_search(query: str) -> str:
    """
    Search the internet and return detailed search results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))  # ✅ fetch more


        if not results:
            return "No search results found."


        # Filter out low quality/irrelevant sites
        filtered = [
            r for r in results
            if not any(blocked in r.get("href", "").lower() for blocked in BLOCKED_SITES)
        ]


        # Fallback to all results if filtering removes everything
        if not filtered:
            filtered = results


        # Take top 4 after filtering
        filtered = filtered[:4]


        output = []
        for i, result in enumerate(filtered, 1):
            output.append(
                f"[{i}] {result['title']}\n"
                f"URL: {result.get('href', 'N/A')}\n"
                f"Summary: {result['body']}"
            )


        return "\n\n".join(output)


    except Exception as e:
        return f"Search Error: {e}"


