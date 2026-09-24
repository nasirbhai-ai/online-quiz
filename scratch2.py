from app import create_app
from app.services.question_suggester import suggest_questions

app = create_app()
with app.app_context():
    data = suggest_questions("General Knowledge", "easy", 5)
    print("Source:", data["source"])
    for q in data["questions"]:
        print(q["text"])
