"""Question suggestion service — fetches and generates MCQs by topic."""

import html
import random
import re
from typing import Dict, List, Optional

import requests

# Open Trivia DB category IDs mapped to common topic keywords
TRIVIA_CATEGORY_MAP = {
    "general": 9,
    "general knowledge": 9,
    "books": 10,
    "literature": 10,
    "film": 11,
    "movies": 11,
    "cinema": 11,
    "music": 12,
    "musicals": 13,
    "theatre": 13,
    "television": 14,
    "tv": 14,
    "video games": 15,
    "gaming": 15,
    "games": 15,
    "science": 17,
    "nature": 17,
    "computers": 18,
    "technology": 18,
    "tech": 18,
    "programming": 18,
    "mathematics": 19,
    "math": 19,
    "maths": 19,
    "mythology": 20,
    "sports": 21,
    "geography": 22,
    "history": 23,
    "politics": 24,
    "art": 25,
    "celebrities": 26,
    "animals": 27,
    "vehicles": 28,
    "comics": 29,
    "comics": 29,
    "gadgets": 30,
    "anime": 31,
    "cartoons": 32,
    "football": 21,
    "basketball": 21,
    "soccer": 21,
    "physics": 17,
    "chemistry": 17,
    "biology": 17,
    "astronomy": 17,
}

# Local fallback questions keyed by broad topic
LOCAL_QUESTION_BANK = {
    "science": [
        {
            "text": "What planet is closest to the Sun?",
            "options": {"A": "Venus", "B": "Mercury", "C": "Mars", "D": "Earth"},
            "correct_option": "B",
            "difficulty": "easy",
        },
        {
            "text": "What gas do plants absorb from the atmosphere?",
            "options": {"A": "Oxygen", "B": "Nitrogen", "C": "Carbon dioxide", "D": "Hydrogen"},
            "correct_option": "C",
            "difficulty": "easy",
        },
        {
            "text": "What is the chemical formula for table salt?",
            "options": {"A": "NaCl", "B": "H2O", "C": "CO2", "D": "CaCO3"},
            "correct_option": "A",
            "difficulty": "medium",
        },
        {
            "text": "Which organelle is responsible for photosynthesis?",
            "options": {"A": "Mitochondria", "B": "Ribosome", "C": "Chloroplast", "D": "Nucleus"},
            "correct_option": "C",
            "difficulty": "medium",
        },
        {
            "text": "What is the unit of electrical resistance?",
            "options": {"A": "Volt", "B": "Ampere", "C": "Ohm", "D": "Watt"},
            "correct_option": "C",
            "difficulty": "hard",
        },
    ],
    "history": [
        {
            "text": "Who was the first man to walk on the Moon?",
            "options": {"A": "Buzz Aldrin", "B": "Neil Armstrong", "C": "Yuri Gagarin", "D": "John Glenn"},
            "correct_option": "B",
            "difficulty": "easy",
        },
        {
            "text": "In which year did the Titanic sink?",
            "options": {"A": "1905", "B": "1912", "C": "1920", "D": "1898"},
            "correct_option": "B",
            "difficulty": "easy",
        },
        {
            "text": "Which empire was ruled by Julius Caesar?",
            "options": {"A": "Greek", "B": "Roman", "C": "Ottoman", "D": "Persian"},
            "correct_option": "B",
            "difficulty": "medium",
        },
        {
            "text": "The Magna Carta was signed in which country?",
            "options": {"A": "France", "B": "England", "C": "Spain", "D": "Germany"},
            "correct_option": "B",
            "difficulty": "hard",
        },
    ],
    "geography": [
        {
            "text": "What is the capital of Japan?",
            "options": {"A": "Seoul", "B": "Beijing", "C": "Tokyo", "D": "Bangkok"},
            "correct_option": "C",
            "difficulty": "easy",
        },
        {
            "text": "Which river flows through Egypt?",
            "options": {"A": "Amazon", "B": "Nile", "C": "Danube", "D": "Ganges"},
            "correct_option": "B",
            "difficulty": "easy",
        },
        {
            "text": "What is the largest desert in the world?",
            "options": {"A": "Sahara", "B": "Gobi", "C": "Antarctic", "D": "Kalahari"},
            "correct_option": "C",
            "difficulty": "medium",
        },
        {
            "text": "Which country has the most time zones?",
            "options": {"A": "USA", "B": "Russia", "C": "France", "D": "China"},
            "correct_option": "C",
            "difficulty": "hard",
        },
    ],
    "technology": [
        {
            "text": "What does CPU stand for?",
            "options": {
                "A": "Central Processing Unit",
                "B": "Computer Personal Unit",
                "C": "Core Program Utility",
                "D": "Central Power Unit",
            },
            "correct_option": "A",
            "difficulty": "easy",
        },
        {
            "text": "Which company developed the Android OS?",
            "options": {"A": "Apple", "B": "Microsoft", "C": "Google", "D": "Samsung"},
            "correct_option": "C",
            "difficulty": "easy",
        },
        {
            "text": "What does SQL stand for?",
            "options": {
                "A": "Structured Query Language",
                "B": "Simple Question Language",
                "C": "System Query Logic",
                "D": "Standard Queue List",
            },
            "correct_option": "A",
            "difficulty": "medium",
        },
        {
            "text": "Which protocol is used to send email?",
            "options": {"A": "HTTP", "B": "FTP", "C": "SMTP", "D": "DNS"},
            "correct_option": "C",
            "difficulty": "hard",
        },
    ],
    "sports": [
        {
            "text": "How many players are on a standard soccer team on the field?",
            "options": {"A": "9", "B": "10", "C": "11", "D": "12"},
            "correct_option": "C",
            "difficulty": "easy",
        },
        {
            "text": "Which country won the FIFA World Cup in 2018?",
            "options": {"A": "Brazil", "B": "Germany", "C": "France", "D": "Argentina"},
            "correct_option": "C",
            "difficulty": "medium",
        },
        {
            "text": "In tennis, what is a score of zero called?",
            "options": {"A": "Nil", "B": "Love", "C": "Zero", "D": "Blank"},
            "correct_option": "B",
            "difficulty": "easy",
        },
    ],
    "movies": [
        {
            "text": "Who directed the movie 'Inception'?",
            "options": {"A": "Steven Spielberg", "B": "Christopher Nolan", "C": "James Cameron", "D": "Quentin Tarantino"},
            "correct_option": "B",
            "difficulty": "medium",
        },
        {
            "text": "Which film won the Academy Award for Best Picture in 2020?",
            "options": {"A": "1917", "B": "Joker", "C": "Parasite", "D": "Once Upon a Time in Hollywood"},
            "correct_option": "C",
            "difficulty": "hard",
        },
    ],
    "cricket": [
        {
            "text": "How many players are in a cricket team on the field?",
            "options": {"A": "9", "B": "10", "C": "11", "D": "12"},
            "correct_option": "C",
            "difficulty": "easy",
        },
        {
            "text": "What is the length of a standard cricket pitch?",
            "options": {"A": "18 yards", "B": "20 yards", "C": "22 yards", "D": "24 yards"},
            "correct_option": "C",
            "difficulty": "medium",
        },
        {
            "text": "Which country won the first ever Cricket World Cup in 1975?",
            "options": {"A": "Australia", "B": "West Indies", "C": "England", "D": "India"},
            "correct_option": "B",
            "difficulty": "hard",
        },
        {
            "text": "What does LBW stand for in cricket?",
            "options": {"A": "Leg Before Wicket", "B": "Long Ball Wide", "C": "Left Batsman Walking", "D": "Leg By Wicket"},
            "correct_option": "A",
            "difficulty": "easy",
        },
        {
            "text": "Who is known as the 'God of Cricket'?",
            "options": {"A": "Ricky Ponting", "B": "Brian Lara", "C": "Sachin Tendulkar", "D": "Don Bradman"},
            "correct_option": "C",
            "difficulty": "medium",
        },
    ],
    "python": [
        {
            "text": "Which keyword is used to define a function in Python?",
            "options": {"A": "func", "B": "def", "C": "function", "D": "define"},
            "correct_option": "B",
            "difficulty": "easy",
        },
        {
            "text": "What data type is the result of: 3 / 2 in Python 3?",
            "options": {"A": "int", "B": "float", "C": "string", "D": "double"},
            "correct_option": "B",
            "difficulty": "medium",
        },
        {
            "text": "Which of these is a mutable data type in Python?",
            "options": {"A": "Tuple", "B": "String", "C": "List", "D": "Integer"},
            "correct_option": "C",
            "difficulty": "easy",
        },
        {
            "text": "What is the output of print(2 ** 3)?",
            "options": {"A": "6", "B": "8", "C": "9", "D": "12"},
            "correct_option": "B",
            "difficulty": "easy",
        },
        {
            "text": "Which decorator is used to define a class method?",
            "options": {"A": "@staticmethod", "B": "@classmethod", "C": "@class", "D": "@method"},
            "correct_option": "B",
            "difficulty": "hard",
        },
    ],
}

# Suggested topics shown in the UI picker
SUGGESTED_TOPICS = [
    "Science",
    "History",
    "Geography",
    "Technology",
    "Sports",
    "Movies",
    "Music",
    "Animals",
    "General Knowledge",
    "Mathematics",
    "Art",
    "Politics",
]


def normalize_topic(topic: str) -> str:
    """Clean and normalize a user-provided topic string."""
    return re.sub(r"\s+", " ", topic.strip())


def resolve_trivia_category(topic: str) -> Optional[int]:
    """Map a topic string to an Open Trivia DB category ID."""
    key = topic.lower().strip()
    if key in TRIVIA_CATEGORY_MAP:
        return TRIVIA_CATEGORY_MAP[key]

    for keyword, cat_id in TRIVIA_CATEGORY_MAP.items():
        if keyword in key or key in keyword:
            return cat_id
    return None


def _decode_trivia_text(text: str) -> str:
    """Decode HTML entities from Open Trivia DB responses."""
    return html.unescape(text or "")


def _format_trivia_question(item: dict, difficulty: str) -> dict:
    """Convert an Open Trivia DB item to our standard question format."""
    correct = _decode_trivia_text(item["correct_answer"])
    incorrect = [_decode_trivia_text(a) for a in item["incorrect_answers"]]

    options_list = [correct] + incorrect
    random.shuffle(options_list)

    letters = ["A", "B", "C", "D"]
    options = {letters[i]: options_list[i] for i in range(4)}
    correct_letter = letters[options_list.index(correct)]

    return {
        "text": _decode_trivia_text(item["question"]),
        "options": options,
        "correct_option": correct_letter,
        "difficulty": difficulty,
        "source": "opentdb",
    }


def fetch_from_opentdb(topic: str, difficulty: str, count: int) -> List[dict]:
    """Fetch questions from the free Open Trivia DB API."""
    category_id = resolve_trivia_category(topic)
    if category_id is None:
        return []

    params = {
        "amount": min(count * 2, 30),
        "category": category_id,
        "difficulty": difficulty,
        "type": "multiple",
    }

    try:
        response = requests.get(
            "https://opentdb.com/api.php",
            params=params,
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    if data.get("response_code") != 0:
        return []

    results = [_format_trivia_question(item, difficulty) for item in data.get("results", [])]
    random.shuffle(results)
    return results[:count]


def _match_local_bank(topic: str) -> Optional[str]:
    """Find the best local question bank for a topic."""
    key = topic.lower().strip()
    if key in LOCAL_QUESTION_BANK:
        return key

    aliases = {
        "science": ["physics", "chemistry", "biology", "astronomy"],
        "history": ["ancient", "world war", "civilization"],
        "geography": ["countries", "capitals", "continents", "maps"],
        "technology": ["computers", "programming", "coding", "software", "tech"],
        "sports": ["football", "basketball", "olympics"],
        "movies": ["film", "cinema", "hollywood", "bollywood"],
        "cricket": ["cricket"],
        "python": ["python", "pythone"],
    }

    for bank_key, keywords in aliases.items():
        if any(kw in key for kw in keywords):
            return bank_key
    return None


def generate_local_questions(topic: str, difficulty: str, count: int) -> List[dict]:
    """Generate questions from the local bank."""
    bank_key = _match_local_bank(topic)
    questions = []

    if bank_key:
        pool = [
            q for q in LOCAL_QUESTION_BANK[bank_key]
            if q["difficulty"] == difficulty
        ]
        if not pool:
            pool = LOCAL_QUESTION_BANK[bank_key]
        questions = random.sample(pool, min(count, len(pool)))

    return [{**q, "source": "local"} for q in questions[:count]]


def suggest_questions(topic: str, difficulty: str = "medium", count: int = 5) -> dict:
    """
    Suggest MCQ questions for a given topic.

    Tries Open Trivia DB first, then fills gaps with local/generated questions.
    Returns a dict with questions and metadata.
    """
    topic = normalize_topic(topic)
    if not topic:
        return {"error": "Topic is required.", "questions": []}

    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "medium"

    count = 10  # Enforce requirement: fetch exactly 10 questions

    questions = fetch_from_opentdb(topic, difficulty, count)
    source = "opentdb" if questions else "local"

    if len(questions) < count:
        local = generate_local_questions(topic, difficulty, count - len(questions))
        questions.extend(local)
        if source == "opentdb" and local:
            source = "mixed"

    if len(questions) < count:
        return {
            "error": f"Could not find enough real questions for topic '{topic}' and difficulty '{difficulty}'. Please try another topic.",
            "questions": []
        }

    return {
        "topic": topic,
        "difficulty": difficulty,
        "count": len(questions),
        "source": source,
        "questions": questions,
    }
