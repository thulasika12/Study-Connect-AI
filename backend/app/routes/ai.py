"""
AI feature routes: doubt-solver chat, note summarizer, quiz generator,
and study planner. All require authentication so usage can be tied to a user.
"""
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.chatbot import solve_doubt
from app.ai.summarizer import summarize_text
from app.ai.quiz_generator import generate_quiz
from app.ai.recommender import generate_study_plan
from app.config.database import get_db
from app.models.chat import AIChat
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.ai_schema import (
    ChatRequest,
    ChatResponse,
    SummarizeRequest,
    SummarizeResponse,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizQuestion,
    StudyPlanRequest,
    StudyPlanResponse,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Features"])


@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI Doubt Solver — student asks an academic question, AI explains the answer."""
    answer = solve_doubt(payload.question)

    chat_record = AIChat(user_id=current_user.id, question=payload.question, answer=answer)
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)

    return ChatResponse(question=payload.question, answer=answer, created_at=chat_record.created_at)


@router.post("/summarize", response_model=SummarizeResponse)
def ai_summarize(
    payload: SummarizeRequest,
    current_user: User = Depends(get_current_user),
):
    """AI Note Summarizer — accepts raw text (from a pasted note or extracted PDF) and returns a summary."""
    summary = summarize_text(payload.text, payload.length)
    return SummarizeResponse(summary=summary)


@router.post("/generate-quiz", response_model=QuizGenerateResponse)
def ai_generate_quiz(
    payload: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI Quiz Generator — generates MCQ questions for a subject/topic, optionally from note text."""
    raw_questions = generate_quiz(
        subject=payload.subject,
        topic=payload.topic,
        num_questions=payload.num_questions,
        source_text=payload.source_text,
    )

    questions = []
    for q in raw_questions:
        questions.append(QuizQuestion(question=q["question"], options=q["options"], answer=q["answer"]))

        # Persist each generated question so students can revisit past quizzes
        db.add(
            Quiz(
                user_id=current_user.id,
                subject=payload.subject,
                topic=payload.topic,
                question=q["question"],
                options=json.dumps(q["options"]),
                answer=q["answer"],
            )
        )
    db.commit()

    return QuizGenerateResponse(subject=payload.subject, topic=payload.topic, questions=questions)


@router.post("/study-plan", response_model=StudyPlanResponse)
def ai_study_plan(
    payload: StudyPlanRequest,
    current_user: User = Depends(get_current_user),
):
    """AI Study Planner — creates a personalized day-by-day study schedule."""
    plan = generate_study_plan(
        subjects=payload.subjects,
        hours_per_day=payload.hours_per_day,
        days=payload.days,
        goal=payload.goal,
    )
    return StudyPlanResponse(plan=plan)
