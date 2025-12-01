# backend/app/agents/router_agent.py
from typing import Dict

class RouterAgent:
    def classify_intent(self, user_input: str) -> str:
        """
        Very simple logic. You can replace with LLM later.
        """
        if "http://" in user_input or "https://" in user_input:
            return "CHECK_USER_NEWS"
        # you can add special keywords for question on previous news
        return "FETCH_NEWS"
