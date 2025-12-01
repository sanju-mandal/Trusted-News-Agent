# backend/app/agents/qa_summary_agent.py
import json
from typing import Dict, List
from ..utils.llm_client import llm_client

SUMMARY_SYSTEM_PROMPT = """
You are a news summarization and Q&A agent.
Given one or more verified news articles, create a short 3-4 sentence, neutral summary which also cover important context.
See the articles carefully to avoid missing key details.
Also, be able to answer specific questions about the news based ONLY on the provided articles.
"""

class QASummaryAgent:
    def summarize(self, articles: List[Dict]) -> str:
        user_prompt = {
            "task": "summary",
            "articles": articles
        }
        raw = llm_client.chat(SUMMARY_SYSTEM_PROMPT, json.dumps(user_prompt))

        try:
            parsed = json.loads(raw)
            return parsed.get("summary", raw)
        except:
            return raw

    def answer_question(self, question: str, context_articles: List[Dict]) -> str:
        user_prompt = {
            "task": "qa",
            "question": question,
            "articles": context_articles
        }
        raw = llm_client.chat(SUMMARY_SYSTEM_PROMPT, json.dumps(user_prompt))

        try:
            parsed = json.loads(raw)
            return parsed.get("answer", raw)
        except:
            return raw