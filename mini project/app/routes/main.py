"""Main routes: home page and leaderboard."""
from flask import Blueprint, render_template
from sqlalchemy import func

from app.extensions import db
from app.models import Score, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing page with platform overview."""
    return render_template("index.html")


@main_bp.route("/leaderboard")
def leaderboard():
    """Display top quiz scores across all users."""
    # Best score per user (highest percentage, then most recent)
    subquery = (
        db.session.query(
            Score.user_id,
            func.max(Score.percentage).label("best_score"),
        )
        .group_by(Score.user_id)
        .subquery()
    )

    top_scores = (
        db.session.query(Score, User)
        .join(User, Score.user_id == User.id)
        .join(
            subquery,
            (Score.user_id == subquery.c.user_id)
            & (Score.percentage == subquery.c.best_score),
        )
        .order_by(Score.percentage.desc(), Score.completed_at.desc())
        .limit(20)
        .all()
    )

    # Recent attempts for activity feed
    recent_scores = (
        Score.query.join(User)
        .order_by(Score.completed_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "leaderboard.html",
        top_scores=top_scores,
        recent_scores=recent_scores,
    )
