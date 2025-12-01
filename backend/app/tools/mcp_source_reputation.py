# backend/app/tools/mcp_source_reputation.py
from typing import Dict

SOURCE_REP_DB = {
    "reuters.com": 0.95,
    "bbc.com": 0.93,
    "ndtv.com": 0.9,
    # low-trust examples:
    "random-fakenews.xyz": 0.1,
}

class SourceReputationTool:
    def check(self, domain: str) -> Dict:
        score = SOURCE_REP_DB.get(domain.lower(), 0.5)
        category = "trusted" if score > 0.8 else "low" if score < 0.3 else "unknown"
        return {"reputation_score": score, "category": category}
