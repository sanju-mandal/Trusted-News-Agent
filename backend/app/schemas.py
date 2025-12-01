# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class NewsQueryRequest(BaseModel):
    user_id: Optional[int] = None
    query: str

class UserNewsCheckRequest(BaseModel):
    user_id: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None

class ArticlePayload(BaseModel):
    article_id: str
    title: str
    content: str
    url: Optional[str] = None
    source_domain: Optional[str] = None

class RealismResult(BaseModel):
    article_id: str
    label: str           # real | fake | uncertain
    confidence: float
    reasons: List[str]
    supporting_sources: List[dict]
    used_tools: List[str]

class NewsResponse(BaseModel):
    topic: str
    summary: str
    articles: list
