"""Seed the database with sample categories and questions."""
from app import create_app
from app.extensions import db
from app.models import Category, Question


def seed_data():
    """Populate categories and MCQ questions."""
    categories_data = [
        {
            "name": "Science",
            "description": "Physics, chemistry, biology, and general science.",
            "questions": [
                {
                    "text": "What is the chemical symbol for water?",
                    "options": ("H2O", "CO2", "O2", "NaCl"),
                    "correct": "A",
                    "difficulty": "easy",
                },
                {
                    "text": "Which planet is known as the Red Planet?",
                    "options": ("Venus", "Mars", "Jupiter", "Saturn"),
                    "correct": "B",
                    "difficulty": "easy",
                },
                {
                    "text": "What is the speed of light in vacuum (approx)?",
                    "options": ("300,000 km/s", "150,000 km/s", "3,000 km/s", "30,000 km/s"),
                    "correct": "A",
                    "difficulty": "medium",
                },
                {
                    "text": "What is the powerhouse of the cell?",
                    "options": ("Nucleus", "Ribosome", "Mitochondria", "Golgi body"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "Which element has the atomic number 1?",
                    "options": ("Helium", "Hydrogen", "Lithium", "Carbon"),
                    "correct": "B",
                    "difficulty": "easy",
                },
                {
                    "text": "What is the SI unit of electric current?",
                    "options": ("Volt", "Ohm", "Ampere", "Watt"),
                    "correct": "C",
                    "difficulty": "medium",
                },
                {
                    "text": "Which scientist proposed the theory of relativity?",
                    "options": ("Newton", "Einstein", "Galileo", "Tesla"),
                    "correct": "B",
                    "difficulty": "medium",
                },
                {
                    "text": "What is the most abundant gas in Earth's atmosphere?",
                    "options": ("Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"),
                    "correct": "C",
                    "difficulty": "medium",
                },
                {
                    "text": "What particle carries a positive charge in an atom?",
                    "options": ("Electron", "Neutron", "Proton", "Photon"),
                    "correct": "C",
                    "difficulty": "hard",
                },
                {
                    "text": "What is the half-life concept primarily used to describe?",
                    "options": ("Star lifespan", "Radioactive decay", "Cell division", "Planetary orbit"),
                    "correct": "B",
                    "difficulty": "hard",
                },
            ],
        },
        {
            "name": "History",
            "description": "World history, civilizations, and major events.",
            "questions": [
                {
                    "text": "In which year did World War II end?",
                    "options": ("1943", "1944", "1945", "1946"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "Who was the first President of the United States?",
                    "options": ("Jefferson", "Washington", "Lincoln", "Adams"),
                    "correct": "B",
                    "difficulty": "easy",
                },
                {
                    "text": "The Great Wall of China was primarily built to protect against invasions from the:",
                    "options": ("Mongols", "Romans", "Persians", "Japanese"),
                    "correct": "A",
                    "difficulty": "medium",
                },
                {
                    "text": "Which ancient civilization built the pyramids at Giza?",
                    "options": ("Romans", "Greeks", "Egyptians", "Mesopotamians"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "The French Revolution began in which year?",
                    "options": ("1776", "1789", "1812", "1848"),
                    "correct": "B",
                    "difficulty": "medium",
                },
                {
                    "text": "Who discovered America in 1492?",
                    "options": ("Magellan", "Columbus", "Vasco da Gama", "Cook"),
                    "correct": "B",
                    "difficulty": "easy",
                },
                {
                    "text": "The Berlin Wall fell in which year?",
                    "options": ("1987", "1989", "1991", "1993"),
                    "correct": "B",
                    "difficulty": "medium",
                },
                {
                    "text": "Which empire was ruled by Genghis Khan?",
                    "options": ("Ottoman", "Mongol", "Roman", "Byzantine"),
                    "correct": "B",
                    "difficulty": "hard",
                },
                {
                    "text": "The Renaissance began in which country?",
                    "options": ("France", "England", "Italy", "Spain"),
                    "correct": "C",
                    "difficulty": "hard",
                },
                {
                    "text": "Who wrote the Declaration of Independence?",
                    "options": ("Franklin", "Jefferson", "Hamilton", "Madison"),
                    "correct": "B",
                    "difficulty": "medium",
                },
            ],
        },
        {
            "name": "Geography",
            "description": "Countries, capitals, landmarks, and physical geography.",
            "questions": [
                {
                    "text": "What is the capital of France?",
                    "options": ("London", "Berlin", "Paris", "Madrid"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "Which is the largest ocean on Earth?",
                    "options": ("Atlantic", "Indian", "Arctic", "Pacific"),
                    "correct": "D",
                    "difficulty": "easy",
                },
                {
                    "text": "Which country has the largest population?",
                    "options": ("USA", "India", "China", "Brazil"),
                    "correct": "B",
                    "difficulty": "medium",
                },
                {
                    "text": "Mount Everest is located in which mountain range?",
                    "options": ("Alps", "Andes", "Himalayas", "Rockies"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "What is the longest river in the world?",
                    "options": ("Amazon", "Nile", "Yangtze", "Mississippi"),
                    "correct": "B",
                    "difficulty": "medium",
                },
                {
                    "text": "Which continent is the Sahara Desert located on?",
                    "options": ("Asia", "Africa", "Australia", "South America"),
                    "correct": "B",
                    "difficulty": "easy",
                },
                {
                    "text": "What is the smallest country in the world?",
                    "options": ("Monaco", "Vatican City", "San Marino", "Liechtenstein"),
                    "correct": "B",
                    "difficulty": "hard",
                },
                {
                    "text": "Which strait separates Europe from Africa?",
                    "options": ("Bering", "Gibraltar", "Malacca", "Bosporus"),
                    "correct": "B",
                    "difficulty": "hard",
                },
                {
                    "text": "What is the capital of Australia?",
                    "options": ("Sydney", "Melbourne", "Canberra", "Perth"),
                    "correct": "C",
                    "difficulty": "medium",
                },
                {
                    "text": "How many countries are in the United Kingdom?",
                    "options": ("2", "3", "4", "5"),
                    "correct": "C",
                    "difficulty": "hard",
                },
            ],
        },
        {
            "name": "Technology",
            "description": "Computers, programming, and modern tech.",
            "questions": [
                {
                    "text": "What does HTML stand for?",
                    "options": (
                        "Hyper Text Markup Language",
                        "High Tech Modern Language",
                        "Hyper Transfer Markup Language",
                        "Home Tool Markup Language",
                    ),
                    "correct": "A",
                    "difficulty": "easy",
                },
                {
                    "text": "Which company created the Python programming language?",
                    "options": ("Microsoft", "Google", "No company — Guido van Rossum", "Apple"),
                    "correct": "C",
                    "difficulty": "medium",
                },
                {
                    "text": "What does CPU stand for?",
                    "options": (
                        "Central Processing Unit",
                        "Computer Personal Unit",
                        "Central Program Utility",
                        "Core Processing Unit",
                    ),
                    "correct": "A",
                    "difficulty": "easy",
                },
                {
                    "text": "Which protocol is used for secure web browsing?",
                    "options": ("HTTP", "FTP", "HTTPS", "SMTP"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "What year was the first iPhone released?",
                    "options": ("2005", "2006", "2007", "2008"),
                    "correct": "C",
                    "difficulty": "medium",
                },
                {
                    "text": "Which data structure uses LIFO (Last In, First Out)?",
                    "options": ("Queue", "Stack", "Tree", "Graph"),
                    "correct": "B",
                    "difficulty": "medium",
                },
                {
                    "text": "What does API stand for?",
                    "options": (
                        "Application Programming Interface",
                        "Advanced Program Integration",
                        "Automated Processing Interface",
                        "Application Process Integration",
                    ),
                    "correct": "A",
                    "difficulty": "easy",
                },
                {
                    "text": "Which language runs in the browser alongside HTML and CSS?",
                    "options": ("Python", "Java", "JavaScript", "C++"),
                    "correct": "C",
                    "difficulty": "easy",
                },
                {
                    "text": "What is the time complexity of binary search?",
                    "options": ("O(n)", "O(log n)", "O(n²)", "O(1)"),
                    "correct": "B",
                    "difficulty": "hard",
                },
                {
                    "text": "Which cloud provider created AWS?",
                    "options": ("Google", "Microsoft", "Amazon", "IBM"),
                    "correct": "C",
                    "difficulty": "hard",
                },
            ],
        },
    ]

    for cat_data in categories_data:
        category = Category.query.filter_by(name=cat_data["name"]).first()
        if category is None:
            category = Category(name=cat_data["name"], description=cat_data["description"])
            db.session.add(category)
            db.session.flush()

        for q_data in cat_data["questions"]:
            existing = Question.query.filter_by(
                category_id=category.id, text=q_data["text"]
            ).first()
            if existing:
                continue

            opts = q_data["options"]
            question = Question(
                category_id=category.id,
                text=q_data["text"],
                option_a=opts[0],
                option_b=opts[1],
                option_c=opts[2],
                option_d=opts[3],
                correct_option=q_data["correct"],
                difficulty=q_data["difficulty"],
            )
            db.session.add(question)

    db.session.commit()
    print("Database seeded successfully!")
    print(f"  Categories: {Category.query.count()}")
    print(f"  Questions:  {Question.query.count()}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()
