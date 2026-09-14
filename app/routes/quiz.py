"""Quiz routes: browse, take, and submit quizzes."""
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Category, Question, Score
from app.services.question_suggester import SUGGESTED_TOPICS
from app.utils import get_quiz_questions

quiz_bp = Blueprint("quiz", __name__)

DIFFICULTIES = ["easy", "medium", "hard"]


def _get_or_create_topic_category(topic: str) -> Category:
    """Find or create a category for a user-chosen topic."""
    category = Category.query.filter(
        db.func.lower(Category.name) == topic.lower()
    ).first()
    if category is None:
        category = Category(name=topic, description=f"Questions about {topic}.")
        db.session.add(category)
        db.session.flush()
    return category


@quiz_bp.route("/suggest")
def suggest_page():
    """Page where users choose a topic and get question suggestions."""
    return render_template("quiz/suggest.html", suggested_topics=SUGGESTED_TOPICS)


@quiz_bp.route("/start-topic-quiz", methods=["POST"])
@login_required
def start_topic_quiz():
    """Start a quiz using suggested questions for a custom topic."""
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON payload."}), 400

    topic = (payload.get("topic") or "").strip()
    difficulty = (payload.get("difficulty") or "medium").lower()
    questions = payload.get("questions") or []

    if not topic:
        return jsonify({"error": "Topic is required."}), 400
    if difficulty not in DIFFICULTIES:
        difficulty = "medium"
    if not questions:
        return jsonify({"error": "No questions provided."}), 400

    max_q = current_app.config.get("MAX_SUGGESTED_QUESTIONS", 15)
    questions = questions[:max_q]

    category = _get_or_create_topic_category(topic)
    db.session.commit()

    # Store custom questions in session (not yet in DB unless user saved them)
    session["quiz"] = {
        "category_id": category.id,
        "category_name": topic,
        "difficulty": difficulty,
        "is_custom": True,
        "custom_questions": [
            {
                "text": q.get("text", ""),
                "options": q.get("options", {}),
                "correct_option": q.get("correct_option", "A").upper(),
            }
            for q in questions
        ],
    }

    return jsonify({"redirect": url_for("quiz.take_quiz")})


@quiz_bp.route("/")
def list_quizzes():
    """Show available quiz categories and difficulty levels."""
    categories = Category.query.order_by(Category.name).all()

    # Count questions per category/difficulty for UI hints
    question_counts = {}
    for cat in categories:
        question_counts[cat.id] = {}
        for diff in DIFFICULTIES:
            count = Question.query.filter_by(
                category_id=cat.id, difficulty=diff
            ).count()
            question_counts[cat.id][diff] = count

    return render_template(
        "quiz/list.html",
        categories=categories,
        difficulties=DIFFICULTIES,
        question_counts=question_counts,
        max_questions=current_app.config.get("QUESTIONS_PER_QUIZ", 5),
    )


@quiz_bp.route("/start/<int:category_id>/<difficulty>")
@login_required
def start_quiz(category_id, difficulty):
    """Initialize a quiz session and redirect to the quiz page."""
    if difficulty not in DIFFICULTIES:
        flash("Invalid difficulty level.", "danger")
        return redirect(url_for("quiz.list_quizzes"))

    category = db.session.get(Category, category_id)
    if category is None:
        flash("Category not found.", "danger")
        return redirect(url_for("quiz.list_quizzes"))

    limit = current_app.config.get("QUESTIONS_PER_QUIZ", 5)
    questions = get_quiz_questions(category_id, difficulty, limit)

    if not questions:
        flash(
            f"No {difficulty} questions available in {category.name}.",
            "warning",
        )
        return redirect(url_for("quiz.list_quizzes"))

    # Store quiz state in server-side session
    session["quiz"] = {
        "category_id": category_id,
        "category_name": category.name,
        "difficulty": difficulty,
        "question_ids": [q.id for q in questions],
        "started_at": None,
    }

    return redirect(url_for("quiz.take_quiz"))


@quiz_bp.route("/take")
@login_required
def take_quiz():
    """Render the interactive quiz page with timer."""
    quiz_data = session.get("quiz")
    if not quiz_data:
        flash("No active quiz. Please select a quiz first.", "warning")
        return redirect(url_for("quiz.list_quizzes"))

    seconds_per_question = current_app.config.get("SECONDS_PER_QUESTION", 30)

    # Custom topic quiz — questions stored in session
    if quiz_data.get("is_custom"):
        custom = quiz_data.get("custom_questions", [])
        questions_payload = [
            {
                "id": f"custom_{i}",
                "text": q["text"],
                "options": q["options"],
            }
            for i, q in enumerate(custom)
        ]
        return render_template(
            "quiz/take.html",
            category_name=quiz_data["category_name"],
            difficulty=quiz_data["difficulty"],
            questions=questions_payload,
            seconds_per_question=seconds_per_question,
            total_questions=len(questions_payload),
        )

    questions = Question.query.filter(
        Question.id.in_(quiz_data["question_ids"])
    ).all()

    # Preserve question order from session
    id_order = {qid: idx for idx, qid in enumerate(quiz_data["question_ids"])}
    questions.sort(key=lambda q: id_order[q.id])

    # Build question payload (exclude correct answers)
    questions_payload = []
    for q in questions:
        questions_payload.append(
            {
                "id": q.id,
                "text": q.text,
                "options": q.get_options(),
            }
        )

    return render_template(
        "quiz/take.html",
        category_name=quiz_data["category_name"],
        difficulty=quiz_data["difficulty"],
        questions=questions_payload,
        seconds_per_question=seconds_per_question,
        total_questions=len(questions_payload),
    )


@quiz_bp.route("/submit", methods=["POST"])
@login_required
def submit_quiz():
    """Grade submitted answers and save the score."""
    quiz_data = session.get("quiz")
    if not quiz_data:
        return jsonify({"error": "No active quiz session."}), 400

    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload."}), 400

    answers = payload.get("answers", {})
    time_taken = payload.get("time_taken", 0)

    correct = 0
    results = []

    # Grade custom topic quiz from session data
    if quiz_data.get("is_custom"):
        custom_questions = quiz_data.get("custom_questions", [])
        for i, question in enumerate(custom_questions):
            qid_str = f"custom_{i}"
            user_answer = answers.get(qid_str, "").upper()
            is_correct = user_answer == question["correct_option"].upper()
            if is_correct:
                correct += 1

            results.append(
                {
                    "question_id": qid_str,
                    "text": question["text"],
                    "user_answer": user_answer or "—",
                    "correct_answer": question["correct_option"],
                    "options": question["options"],
                    "is_correct": is_correct,
                }
            )
        total = len(custom_questions)
    else:
        question_ids = quiz_data["question_ids"]
        questions = Question.query.filter(Question.id.in_(question_ids)).all()
        question_map = {q.id: q for q in questions}

        for qid in question_ids:
            qid_str = str(qid)
            user_answer = answers.get(qid_str, "").upper()
            question = question_map.get(qid)

            if question is None:
                continue

            is_correct = user_answer == question.correct_option.upper()
            if is_correct:
                correct += 1

            results.append(
                {
                    "question_id": qid,
                    "text": question.text,
                    "user_answer": user_answer or "—",
                    "correct_answer": question.correct_option,
                    "options": question.get_options(),
                    "is_correct": is_correct,
                }
            )
        total = len(question_ids)

    percentage = round((correct / total) * 100, 1) if total > 0 else 0

    score = Score(
        user_id=current_user.id,
        category_id=quiz_data["category_id"],
        difficulty=quiz_data["difficulty"],
        total_questions=total,
        correct_answers=correct,
        percentage=percentage,
        time_taken=int(time_taken),
    )
    db.session.add(score)
    db.session.commit()

    # Clear quiz session
    session.pop("quiz", None)

    return jsonify(
        {
            "score_id": score.id,
            "correct": correct,
            "total": total,
            "percentage": percentage,
            "results": results,
            "redirect": url_for("quiz.show_result", score_id=score.id),
        }
    )


@quiz_bp.route("/result/<int:score_id>")
@login_required
def show_result(score_id):
    """Display quiz results after submission."""
    score = db.session.get(Score, score_id)

    if score is None:
        abort(404)
    if score.user_id != current_user.id:
        abort(403)

    return render_template("quiz/result.html", score=score)
