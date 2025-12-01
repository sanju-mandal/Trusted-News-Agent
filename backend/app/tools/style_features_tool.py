# backend/app/tools/style_features_tool.py
import re
from typing import Dict

class StyleFeaturesTool:
    def compute(self, text: str) -> Dict:
        exclamations = text.count("!")
        all_caps_words = len([w for w in text.split() if w.isupper() and len(w) > 3])
        clickbait_phrases = ["shocking", "you won't believe", "unbelievable"]
        clickbait_hits = sum(1 for p in clickbait_phrases if p.lower() in text.lower())

        return {
            "exclamations": exclamations,
            "all_caps_words": all_caps_words,
            "clickbait_hits": clickbait_hits,
        }
