import os
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# search = BraveSearch.from_api_key(
#     api_key=os.getenv("BRAVE_SEARCH_API_KEY"),
#     search_kwargs={"count": 5}
# )
brave_search = DuckDuckGoSearchRun() 