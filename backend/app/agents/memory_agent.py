# backend/app/agents/memory_agent.py
import json
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from .. import models

class MemoryAgent:
    def save_interaction(
        self,
        db: Session,
        *,
        user_id: Optional[int],
        type: str,
        topic: Optional[str],
        article_or_text: Dict,
        realism_result: Dict,
        summary: Optional[str],
    ):
        interaction = models.NewsInteraction(
            user_id=user_id,
            type=type,
            topic=topic,
            title=article_or_text.get("title"),
            url=article_or_text.get("url"),
            raw_text=article_or_text.get("content") or article_or_text.get("text"),
            label=realism_result.get("label"),
            confidence=realism_result.get("confidence"),
            summary=json.dumps(summary) if isinstance(summary, dict) else summary,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    def get_recent_interactions(self, db: Session, user_id: int, limit: int = 10):
        return (
            db.query(models.NewsInteraction)
            .filter(models.NewsInteraction.user_id == user_id)
            .order_by(models.NewsInteraction.created_at.desc())
            .limit(limit)
            .all()
        )
