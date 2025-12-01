# backend/app/agents/realism_agent.py
import json
from typing import Dict
from ..tools.mcp_source_reputation import SourceReputationTool
from ..tools.style_features_tool import StyleFeaturesTool
from ..utils.llm_client import llm_client

REALISM_SYSTEM_PROMPT = """
You are a Realism Checker Agent in a news verification system.
Decide if a news article is likely real, fake, or uncertain.
Use evidence from tools: source reputation, style features, and any provided similar news/fact-check data.
Be cautious. Search carefully across all evidence before making a decision from the article or source alone which will be provided. Accordingly, provide clear reasons for your decision.
Respond ONLY as valid JSON with keys: label, confidence, reasons, supporting_sources.
"""

class RealismCheckerAgent:
    def __init__(self,
                 src_rep_tool: SourceReputationTool,
                 style_tool: StyleFeaturesTool):
        self.src_rep_tool = src_rep_tool
        self.style_tool = style_tool

    def check_article(self, article: Dict) -> Dict:
        # article keys: article_id, title, content, url, source_domain
        src_info = self.src_rep_tool.check(article.get("source_domain", ""))
        style_feats = self.style_tool.compute(article.get("content", ""))

        user_prompt = json.dumps({
            "article": article,
            "source_reputation": src_info,
            "style_features": style_feats,
            # you can add factcheck/similar_news later
        })

        raw = llm_client.chat(REALISM_SYSTEM_PROMPT, user_prompt)

        print("\n\n===== USER PROMPT SENT TO LLM =====")
        print(user_prompt)
        print("===== END USER PROMPT =====\n\n")


        print("\n\n===== RAW LLM OUTPUT =====")
        print(raw)
        print("===== END RAW OUTPUT =====\n\n")


        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {
                "label": "uncertain",
                "confidence": 0.5,
                "reasons": ["LLM output not valid JSON"],
                "supporting_sources": []
            }

        reasons = parsed.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]
        elif isinstance(reasons, dict):
            reasons = [json.dumps(reasons)]
        elif not isinstance(reasons, list):
            reasons = [str(reasons)]

        result = {
            "article_id": article["article_id"],
            "label": parsed.get("label", "uncertain"),
            "confidence": float(parsed.get("confidence", 0.5)),
            "reasons": reasons,
            "supporting_sources": parsed.get("supporting_sources", []),
            "used_tools": ["mcp_source_reputation", "style_features_tool"]
        }
        return result
