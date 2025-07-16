import os
import re
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Literal

from dotenv import load_dotenv
from fastapi import APIRouter, Body, Depends, FastAPI, status
from pydantic import BaseModel
from caseconverter import camelcase


POSITIVE_PATTERNS = [r'\bхорош\w*', r'\bлюблю\w*']
NEGATIVE_PATTERNS = [r'\bплохо\w*', r'\bненавиж\w*']
CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    created_at TEXT NOT NULL
);
'''


# Env vars
load_dotenv()
SQLITE_PATH = os.getenv('SQLITE_PATH')


# init db
def init_db():
    with sqlite3.connect(SQLITE_PATH) as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# Define app and router
app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix='/reviews')


# Models
class ReviewRequest(BaseModel, alias_generator=camelcase):
    text: str


ReviewRequestBody = Annotated[ReviewRequest, Body()]


class ReviewFilter(BaseModel, alias_generator=camelcase):
    sentiment: Literal['positive', 'negative', 'neutral'] | None = None


ReviewFilterQuery = Annotated[ReviewFilter, Depends()]


class ReviewResponse(BaseModel, alias_generator=camelcase, populate_by_name=True):
    id: int
    text: str
    sentiment: str
    created_at: str


# Sentiment analysis
def analyze_sentiment(text: str) -> str:
    text = text.lower()

    if any(re.search(p, text) for p in POSITIVE_PATTERNS):
        return 'positive'
    if any(re.search(p, text) for p in NEGATIVE_PATTERNS):
        return 'negative'
    return 'neutral'


# Endpoints
@router.post('', status_code=status.HTTP_201_CREATED, response_model=ReviewResponse)
async def post_review(review: ReviewRequestBody):
    sentiment = analyze_sentiment(review.text)
    created_at = datetime.utcnow().isoformat()

    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
            (review.text, sentiment, created_at),
        )
        conn.commit()
        review_id = cursor.lastrowid

    return ReviewResponse(
        id=review_id,
        text=review.text,
        sentiment=sentiment,
        created_at=created_at
    )


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ReviewResponse])
async def get_review(query: ReviewFilterQuery):
    sql = 'SELECT id, text, sentiment, created_at FROM reviews'
    params = (query.sentiment,) if query.sentiment else ()

    if query.sentiment:
        sql += ' WHERE sentiment = ?'

    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return [
        ReviewResponse(id=r[0], text=r[1], sentiment=r[2], created_at=r[3])
        for r in rows
    ]


# Include routers
app.include_router(router)
