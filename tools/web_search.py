from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool


_duckduckgo_search = DuckDuckGoSearchRun()


@tool("web_search")
def web_search(query: str) -> str:
    """
    Search the public web for current or external information.

    This tool uses DuckDuckGo. It is the only web search tool available in
    CFO Buddy; do not call brave_search or any provider-specific search tool.
    """
    return _duckduckgo_search.run(query)
