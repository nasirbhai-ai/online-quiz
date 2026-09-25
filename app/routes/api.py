"""API routes for question suggestions."""

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Category, Question
from app.services.question_suggester import SUGGESTED_TOPICS, suggest_questions

api_bp = Blueprint("api", __name__)


@api_bp.route("/topics", methods=["GET"])
def list_topics():
    """Return suggested topics and existing categories."""
    categories = Category.query.order_by(Category.name).all()
    return jsonify({
        "suggested_topics": SUGGESTED_TOPICS,
        "categories": [{"id": c.id, "name": c.name} for c in categories],
    })


@api_bp.route("/suggest-questions", methods=["POST"])
def suggest_questions_api():
    """
    Suggest new MCQ questions for a user-chosen topic.

    JSON body:
        topic (str, required): e.g. "Science", "Cricket", "Space"
        difficulty (str): easy | medium | hard (default: medium)
        count (int): number of questions, 1-15 (default: 5)
    """
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON payload."}), 400

    topic = (data.get("topic") or "").strip()
    difficulty = (data.get("difficulty") or "medium").lower()
    count = data.get("count", current_app.config.get("QUESTIONS_PER_QUIZ", 10))

    if not topic:
        return jsonify({"error": "Please provide a topic."}), 400

    try:
        count = int(count)
    except (TypeError, ValueError):
        return jsonify({"error": "Count must be a number."}), 400

    result = suggest_questions(topic, difficulty, count)

    if result.get("error"):
        return jsonify(result), 400

    return jsonify(result)


@api_bp.route("/save-question", methods=["POST"])
@login_required
def save_suggested_question():
    """Save a suggested question to the database under the chosen topic category."""
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON payload."}), 400

    topic = (data.get("topic") or "").strip()
    text = (data.get("text") or "").strip()
    options = data.get("options") or {}
    correct_option = (data.get("correct_option") or "").upper()
    difficulty = (data.get("difficulty") or "medium").lower()

    if not all([topic, text, correct_option]):
        return jsonify({"error": "Topic, question text, and correct answer are required."}), 400

    if correct_option not in ("A", "B", "C", "D"):
        return jsonify({"error": "Correct option must be A, B, C, or D."}), 400

    for letter in ("A", "B", "C", "D"):
        if not options.get(letter, "").strip():
            return jsonify({"error": f"Option {letter} is required."}), 400

    # Find or create category for this topic
    category = Category.query.filter(
        db.func.lower(Category.name) == topic.lower()
    ).first()

    if category is None:
        category = Category(name=topic, description=f"User-suggested questions about {topic}.")
        db.session.add(category)
        db.session.flush()

    # Avoid exact duplicates
    existing = Question.query.filter_by(category_id=category.id, text=text).first()
    if existing:
        return jsonify({"error": "This question already exists in the database.", "question_id": existing.id}), 409

    question = Question(
        category_id=category.id,
        text=text,
        option_a=options["A"].strip(),
        option_b=options["B"].strip(),
        option_c=options["C"].strip(),
        option_d=options["D"].strip(),
        correct_option=correct_option,
        difficulty=difficulty if difficulty in ("easy", "medium", "hard") else "medium",
    )
    db.session.add(question)
    db.session.commit()

    return jsonify({
        "message": "Question saved successfully.",
        "question_id": question.id,
        "category_id": category.id,
        "category_name": category.name,
    }), 201
