from app import create_app
from app.extensions import db
from app.models import Category, Question
from app.utils import get_quiz_questions

app = create_app()
with app.app_context():
    # Make sure we have a category
    cat = Category.query.first()
    if cat:
        print(f"Testing with category: {cat.name}")
        questions = get_quiz_questions(cat.id, 'easy', 5)
        print(f"Got {len(questions)} questions")
        for q in questions:
            print(f"Q: {q.id} - {q.text}")
    else:
        print("No category found.")
