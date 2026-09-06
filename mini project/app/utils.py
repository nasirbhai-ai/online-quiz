"""Utility helpers for the quiz platform."""
import re

from flask import current_app

from app.extensions import db
from app.models import Question


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Username must be 3-20 alphanumeric characters."""
    return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))


def get_quiz_questions(category_id: int, difficulty: str, limit: int = None):
    """
    Fetch random questions for a quiz attempt.
    Generates new ones if empty or not enough.
    """
    if limit is None:
        limit = current_app.config.get("QUESTIONS_PER_QUIZ", 10)

    from app.models import Category
    from app.services.question_suggester import suggest_questions

    questions = (
        Question.query.filter_by(category_id=category_id, difficulty=difficulty)
        .order_by(db.func.random())
        .limit(limit)
        .all()
    )
    
    if len(questions) < limit:
        category = db.session.get(Category, category_id)
        if category:
            needed = limit - len(questions)
            sugg_data = suggest_questions(category.name, difficulty, needed)
            for q_data in sugg_data.get("questions", []):
                text = q_data.get("text", "").strip()
                if not text:
                    continue
                existing = Question.query.filter_by(category_id=category.id, text=text).first()
                if not existing:
                    opts = q_data.get("options", {})
                    new_q = Question(
                        category_id=category.id,
                        text=text,
                        option_a=opts.get("A", "A").strip(),
                        option_b=opts.get("B", "B").strip(),
                        option_c=opts.get("C", "C").strip(),
                        option_d=opts.get("D", "D").strip(),
                        correct_option=q_data.get("correct_option", "A").upper(),
                        difficulty=difficulty,
                    )
                    db.session.add(new_q)
                    questions.append(new_q)
            db.session.commit()

    return questions[:limit]
