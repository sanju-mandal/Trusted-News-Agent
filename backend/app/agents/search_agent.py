# backend/app/agents/search_agent.py
from typing import List, Dict
from ..tools.mcp_google_search import GoogleSearchTool

class SearchAgent:
    def __init__(self, search_tool: GoogleSearchTool):
        self.search_tool = search_tool

    async def fetch_articles(self, topic: str) -> List[Dict]:
        return await self.search_tool.search_news(topic)
