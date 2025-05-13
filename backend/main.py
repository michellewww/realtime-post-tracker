from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import datetime
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import json
from pydantic import BaseModel
from typing import List

from models import Subscription
from database import SessionLocal, engine
from models import Base
from scheduler import start_scheduler
from email_utils import send_email
from news_crawler import NewsCrawler

class SearchQuery(BaseModel):
    query: str

class NewsQuery(BaseModel):
    keywords: List[str]

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/subscribe")
def subscribe(
    email: str = Form(...),
    topic: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(Subscription).filter_by(email=email, topic=topic).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed to this topic")

    sub = Subscription(email=email, topic=topic, interval_minutes=1)
    db.add(sub)
    db.commit()
    send_email(
        subject=f"Subscribed to '{topic}'",
        body=f"You'll receive updates about '{topic}' every 15 minutes.",
        sender="your_email@gmail.com",
        recipients=[email],
    )
    return {"message": f"Subscribed to '{topic}' successfully."}

@app.get("/api/updates")
def get_updates(email: str, topic: str, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter_by(email=email, topic=topic).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"sent_ids": sub.sent_ids.split(',')}

@app.post("/api/news")
def get_news(query: NewsQuery):
    crawler = NewsCrawler()
    articles = crawler.search_news(query.keywords)
    
    # Debug output
    print("DEBUG - Keywords received:", query.keywords)
    print("DEBUG - Number of articles found:", len(articles))
    for i, article in enumerate(articles):
        print(f"DEBUG - Article {i+1}:")
        print(f"  Title: {article['title']}")
        print(f"  Source: {article['source']}")
        print(f"  URL: {article['url']}")
    
    return {"articles": articles}

@app.post("/api/search")
def search(query: SearchQuery):
    # Simple keyword extraction
    query_text = query.query.strip()
    
    # Make sure to extract meaningful keywords
    if not query_text:
        return {"keywords": []}
    
    # Simply split the query if it contains multiple words
    if " " in query_text:
        # Extract keywords by splitting on spaces and filtering out empty strings
        keywords = [word.strip() for word in query_text.split() if word.strip()]
    else:
        # For single-word queries, just use the query as a keyword
        keywords = [query_text]
    
    print(f"DEBUG - Extracted keywords from '{query_text}': {keywords}")
    return {"keywords": keywords}

if __name__ == "__main__":
    import uvicorn
    start_scheduler()
    uvicorn.run(app, host="0.0.0.0", port=8000)
