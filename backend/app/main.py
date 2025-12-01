# backend/app/main.py
import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from dotenv import load_dotenv
load_dotenv()

from .database import Base, engine, SessionLocal
from . import models, schemas
from .agents.search_agent import SearchAgent
from .agents.realism_agent import RealismCheckerAgent
from .agents.qa_summary_agent import QASummaryAgent
from .agents.memory_agent import MemoryAgent
from .agents.router_agent import RouterAgent
from .tools.mcp_google_search import GoogleSearchTool
from .tools.mcp_source_reputation import SourceReputationTool
from .tools.style_features_tool import StyleFeaturesTool

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic AI News Verifier & Summarizer")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- dependencies ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- construct agents/tools ----
search_tool = GoogleSearchTool(api_key=os.getenv("YOUR_API_KEY"), cx=os.getenv("YOUR_CX"))
search_agent = SearchAgent(search_tool)
realism_agent = RealismCheckerAgent(SourceReputationTool(), StyleFeaturesTool())
qa_summary_agent = QASummaryAgent()
memory_agent = MemoryAgent()
router_agent = RouterAgent()

# ---------- ROUTES ----------

@app.post("/api/news/query")
async def query_news(req: schemas.NewsQueryRequest, db: Session = Depends(get_db)):
    """
    User asks: 'Give me latest real news about X'
    """
    topic = req.query

    # 1) fetch articles
    articles = await search_agent.fetch_articles(topic)

    #For check the working
    print("ARTICLES FETCHED:", articles)


    # 2) realism check on each
    checked = []
    for art in articles[:3]:
        result = realism_agent.check_article(art)
        checked.append((art, result))

    #For check the working
    print("REALISM RESULTS: ", checked)

    # 3) keep only real & high confidence
    trusted = [
        (a, r) for (a, r) in checked
        if ( r["label"] == "real" and r["confidence"] >= 0.5 ) or ( r["label"] == "uncertain" and r["confidence"] <= 0.5 )
    ]

    #r["label"] == "real"

    if not trusted:
        return {"topic": topic, "summary": "No strongly trusted news found.", "articles": []}

    trusted_articles = [a for (a, _) in trusted]

    # 4) summarize
    summary_text = qa_summary_agent.summarize(trusted_articles)

    # 5) save first trusted article in memory (you can loop for all)
    for a, r in trusted:
        memory_agent.save_interaction(
            db,
            user_id=req.user_id,
            type="search",
            topic=topic,
            article_or_text=a,
            realism_result=r,
            summary=summary_text,
        )

    return {
        "topic": topic,
        "summary": summary_text,
        "articles": [
            {
                "title": a["title"],
                "url": a["url"],
                "source_domain": a["source_domain"],
                "label": r["label"],
                "confidence": r["confidence"],
            }
            for a, r in trusted
        ],
    }


#Changes made here 

@app.post("/api/users/create")
def create_user(name: str, db: Session = Depends(get_db)):
    user = models.User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user with ID: {user.id}")
    return {"status": "success", "user_id": user.id}



@app.post("/api/news/check")
async def check_user_news(req: schemas.UserNewsCheckRequest, db: Session = Depends(get_db)):
    """
    User pastes a news text or URL.
    """
    # FIXME: if url provided, you should fetch the page content first.
    article = {
        "article_id": "user-1",
        "title": req.title or (req.text[:70] if req.text else ""),
        "content": req.text or "",
        "url": req.url,
        "source_domain": req.url.split("/")[2] if req.url else "",
    }

    realism_result = realism_agent.check_article(article)

    # optional summary on demand (for now, just always generate a tiny one)
    summary_text = qa_summary_agent.summarize([article])

    memory_agent.save_interaction(
        db,
        user_id=req.user_id,
        type="user_input",
        topic=None,
        article_or_text=article,
        realism_result=realism_result,
        summary=summary_text,
    )

    return {
        "verdict": realism_result,
        "summary": summary_text,
    }

@app.get("/api/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    interactions = memory_agent.get_recent_interactions(db, user_id=user_id)
    return [
        {
            "id": i.id,
            "type": i.type,
            "topic": i.topic,
            "title": i.title,
            "url": i.url,
            "label": i.label,
            "confidence": i.confidence,
            "summary": i.summary,
            "created_at": i.created_at,
        }
        for i in interactions
    ]


@app.delete("/api/history/delete/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(models.NewsInteraction).filter(
        models.NewsInteraction.id == interaction_id
    ).first()

    if not interaction:
        return {"status": "error", "message": "Interaction not found"}

    db.delete(interaction)
    db.commit()
    return {"status": "success", "deleted_id": interaction_id}
