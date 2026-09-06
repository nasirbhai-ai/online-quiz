"""Application configuration."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for the quiz platform."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-quiz-platform-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'quiz.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Quiz settings
    SECONDS_PER_QUESTION = 30
    QUESTIONS_PER_QUIZ = 10
    MAX_SUGGESTED_QUESTIONS = 15
