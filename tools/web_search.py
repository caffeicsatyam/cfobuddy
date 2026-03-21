import os
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

web_search = DuckDuckGoSearchRun() 