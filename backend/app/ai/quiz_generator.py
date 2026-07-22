"""
AI Quiz Generator — produces MCQ questions from a subject/topic, or from
supplied source text (e.g. a note's content), returned as strict JSON.
"""
import json
from typing import List, Optional

from fastapi import HTTPException

from app.services.ai_service import chat_completion

SYSTEM_PROMPT = (
    "You are an expert exam question setter. Generate multiple-choice questions (MCQs) "
    "strictly as a JSON array and nothing else — no markdown, no commentary, no code fences. "
    "Each item must have exactly this shape: "
    '{"question": "string", "options": ["A", "B", "C", "D"], "answer": "the correct option text"}. '
    "Options must be plausible and only one should be correct."
)


def generate_quiz(subject: str, topic: str, num_questions: int = 5, source_text: Optional[str] = None) -> List[dict]:
    if source_text:
        user_prompt = (
            f"Generate {num_questions} MCQ questions about the subject '{subject}', topic '{topic}', "
            f"based strictly on the following study material:\n\n{source_text}"
        )
    else:
        user_prompt = (
            f"Generate {num_questions} MCQ questions for the subject '{subject}' on the topic '{topic}', "
            "suitable for a student revising this topic."
        )

    raw = chat_completion(SYSTEM_PROMPT, user_prompt, temperature=0.4)

    # Defensive parsing in case the model wraps JSON in code fences
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        questions = json.loads(cleaned)
        if not isinstance(questions, list):
            raise ValueError("Expected a JSON array")
        return questions
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"AI returned an unexpected format: {exc}") from exc
