"""
Pydantic schemas for the AI features: chat, summarizer, quiz generator,
and study planner.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    question: str
    answer: str
    created_at: datetime


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=10)
    length: Optional[str] = Field(default="medium", description="short | medium | long")


class SummarizeResponse(BaseModel):
    summary: str


class QuizGenerateRequest(BaseModel):
    subject: str
    topic: str
    num_questions: int = Field(default=5, ge=1, le=20)
    source_text: Optional[str] = None


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


class QuizGenerateResponse(BaseModel):
    subject: str
    topic: str
    questions: List[QuizQuestion]


class StudyPlanRequest(BaseModel):
    subjects: List[str]
    hours_per_day: float = Field(default=2, ge=0.5, le=16)
    days: int = Field(default=7, ge=1, le=90)
    goal: Optional[str] = None


class StudyPlanDay(BaseModel):
    day: int
    tasks: List[str]


class StudyPlanResponse(BaseModel):
    plan: List[StudyPlanDay]
