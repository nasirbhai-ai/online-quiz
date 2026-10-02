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
        # Easy
        {"text": "How many players are in a cricket team on the field?", "options": {"A": "9", "B": "10", "C": "11", "D": "12"}, "correct_option": "C", "difficulty": "easy"},
        {"text": "What is the length of a standard cricket pitch?", "options": {"A": "18 yards", "B": "20 yards", "C": "22 yards", "D": "24 yards"}, "correct_option": "C", "difficulty": "easy"},
        {"text": "What does LBW stand for in cricket?", "options": {"A": "Leg Before Wicket", "B": "Long Ball Wide", "C": "Left Batsman Walking", "D": "Leg By Wicket"}, "correct_option": "A", "difficulty": "easy"},
        {"text": "Which tool is used by the batsman to hit the ball?", "options": {"A": "Racket", "B": "Bat", "C": "Stick", "D": "Club"}, "correct_option": "B", "difficulty": "easy"},
        {"text": "How many bails are placed on a set of stumps?", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "correct_option": "B", "difficulty": "easy"},
        {"text": "What is it called when a bowler takes 3 wickets in 3 consecutive balls?", "options": {"A": "Triple play", "B": "Hat-trick", "C": "Strike", "D": "Super-over"}, "correct_option": "B", "difficulty": "easy"},
        {"text": "Which player throws the ball to the batsman?", "options": {"A": "Fielder", "B": "Wicketkeeper", "C": "Umpire", "D": "Bowler"}, "correct_option": "D", "difficulty": "easy"},
        {"text": "What is the cricket format that lasts for 20 overs per side?", "options": {"A": "Test", "B": "ODI", "C": "T10", "D": "T20"}, "correct_option": "D", "difficulty": "easy"},
        {"text": "What does the umpire signal when the ball crosses the boundary without bouncing?", "options": {"A": "Four", "B": "Six", "C": "Wide", "D": "No ball"}, "correct_option": "B", "difficulty": "easy"},
        {"text": "Who stands behind the stumps on the batting side?", "options": {"A": "Bowler", "B": "Captain", "C": "Wicketkeeper", "D": "Umpire"}, "correct_option": "C", "difficulty": "easy"},
        
        # Medium
        {"text": "Who is known as the 'God of Cricket'?", "options": {"A": "Ricky Ponting", "B": "Brian Lara", "C": "Sachin Tendulkar", "D": "Don Bradman"}, "correct_option": "C", "difficulty": "medium"},
        {"text": "Which country won the first ever Cricket World Cup in 1975?", "options": {"A": "Australia", "B": "West Indies", "C": "England", "D": "India"}, "correct_option": "B", "difficulty": "medium"},
        {"text": "The famous Ashes series is played between which two countries?", "options": {"A": "India and Pakistan", "B": "England and Australia", "C": "South Africa and New Zealand", "D": "West Indies and England"}, "correct_option": "B", "difficulty": "medium"},
        {"text": "How many legitimate deliveries make up a standard over?", "options": {"A": "4", "B": "5", "C": "6", "D": "8"}, "correct_option": "C", "difficulty": "medium"},
        {"text": "What is an over in which no runs are scored off the bat called?", "options": {"A": "Empty over", "B": "Blank over", "C": "Zero over", "D": "Maiden over"}, "correct_option": "D", "difficulty": "medium"},
        {"text": "How often is the ICC Cricket World Cup (ODI) held?", "options": {"A": "Every 2 years", "B": "Every 3 years", "C": "Every 4 years", "D": "Every 5 years"}, "correct_option": "C", "difficulty": "medium"},
        {"text": "What is the term for a batsman scoring 100 runs in a single innings?", "options": {"A": "Half-century", "B": "Century", "C": "Double century", "D": "Ton"}, "correct_option": "B", "difficulty": "medium"},
        {"text": "Which team has won the most ICC Men's ODI World Cups?", "options": {"A": "India", "B": "West Indies", "C": "Australia", "D": "England"}, "correct_option": "C", "difficulty": "medium"},
        {"text": "What is the maximum number of overs a single bowler can bowl in a standard ODI match?", "options": {"A": "8", "B": "10", "C": "12", "D": "20"}, "correct_option": "B", "difficulty": "medium"},
        {"text": "What happens if a bowler bowls a delivery that is too high or too wide?", "options": {"A": "Free hit", "B": "No ball", "C": "Wide ball", "D": "Dead ball"}, "correct_option": "C", "difficulty": "medium"},

        # Hard
        {"text": "In which year was the first officially recognized Test match played?", "options": {"A": "1877", "B": "1882", "C": "1895", "D": "1901"}, "correct_option": "A", "difficulty": "hard"},
        {"text": "Who won the inaugural ICC T20 World Cup in 2007?", "options": {"A": "Pakistan", "B": "India", "C": "Sri Lanka", "D": "Australia"}, "correct_option": "B", "difficulty": "hard"},
        {"text": "What was Sir Donald Bradman's final Test batting average?", "options": {"A": "98.99", "B": "99.94", "C": "100.00", "D": "101.22"}, "correct_option": "B", "difficulty": "hard"},
        {"text": "Who holds the record for the highest individual score in a Test innings (400 not out)?", "options": {"A": "Matthew Hayden", "B": "Virender Sehwag", "C": "Brian Lara", "D": "Gary Sobers"}, "correct_option": "C", "difficulty": "hard"},
        {"text": "In which Cricket World Cup were white balls and colored clothing introduced?", "options": {"A": "1983", "B": "1987", "C": "1992", "D": "1996"}, "correct_option": "C", "difficulty": "hard"},
        {"text": "Who holds the record for the most wickets in Test cricket history?", "options": {"A": "Shane Warne", "B": "Anil Kumble", "C": "Muttiah Muralitharan", "D": "James Anderson"}, "correct_option": "C", "difficulty": "hard"},
        {"text": "The Duckworth-Lewis-Stern (DLS) method is primarily used for?", "options": {"A": "Calculating player rankings", "B": "Adjusting targets in rain-affected matches", "C": "Reviewing umpire decisions", "D": "Measuring pitch moisture"}, "correct_option": "B", "difficulty": "hard"},
        {"text": "Who was the first batsman to score a double century in a men's ODI match?", "options": {"A": "Virender Sehwag", "B": "Rohit Sharma", "C": "Sachin Tendulkar", "D": "Martin Guptill"}, "correct_option": "C", "difficulty": "hard"},
        {"text": "What is 'Mankading' in cricket?", "options": {"A": "Running out the non-striker before bowling", "B": "Hitting the ball twice", "C": "Obstructing the field", "D": "Handling the ball"}, "correct_option": "A", "difficulty": "hard"},
        {"text": "The longest cricket match ever played, known as the 'Timeless Test', was between England and which country?", "options": {"A": "Australia", "B": "West Indies", "C": "South Africa", "D": "India"}, "correct_option": "C", "difficulty": "hard"},
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
        "amount": count,
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

def generate_wikipedia_questions(topic: str, difficulty: str, count: int) -> list:
    """Generate basic fallback questions from Wikipedia summaries."""
    questions = []
    
    # Try the specific topic first, then broad ones to ensure we get enough questions
    topics_to_try = [topic, "History", "Science", "Technology", "General knowledge"]
    
    for current_topic in topics_to_try:
        if len(questions) >= count:
            break
            
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={current_topic}&utf8=&format=json&srlimit=1"
        headers = {'User-Agent': 'QuizApp/1.0'}
        
        try:
            search_res = requests.get(search_url, headers=headers, timeout=5).json()
            search_results = search_res.get("query", {}).get("search", [])
            if not search_results:
                continue
            title = search_results[0]["title"]
        except Exception:
            continue

        extract_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exlimit=1&titles={title}&explaintext=1&format=json"
        try:
            extract_res = requests.get(extract_url, headers=headers, timeout=5).json()
            pages = extract_res.get("query", {}).get("pages", {})
            page = list(pages.values())[0]
            text = page.get("extract", "")
            if not text:
                continue
        except Exception:
            continue

        text = re.sub(r'==.*?==', '', text)
        text = re.sub(r'\n+', ' ', text)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if 5 < len(s.split()) < 30]

        all_words = []
        for s in sentences:
            words = [w for w in re.findall(r'\b[A-Z][a-z]+\b|\b\d{2,}\b', s) if len(w) > 3]
            all_words.extend(words)
        all_words = list(set(all_words))

        random.shuffle(sentences)
        
        for s in sentences:
            if len(questions) >= count:
                break
                
            words = s.split()
            candidates = []
            for i, w in enumerate(words):
                if i == 0: continue
                clean_w = re.sub(r'[^\w]', '', w)
                if (clean_w.istitle() and clean_w.isalpha() and len(clean_w) > 3) or (clean_w.isdigit() and len(clean_w) >= 2):
                    candidates.append((i, clean_w))
                    
            if candidates:
                idx, ans = random.choice(candidates)
                q_words = words[:]
                q_words[idx] = "_____"
                q_text = " ".join(q_words)
                
                distractors = [w for w in all_words if w != ans and (w.isdigit() == ans.isdigit())]
                generic_distractors = ["None", "Unknown", "Not specified", "Various", "Multiple", "One", "Two", "Three"]
                if ans.isdigit():
                    generic_distractors = [str(int(ans) + random.randint(1, 10)) for _ in range(3)]
                    
                for gd in generic_distractors:
                    if len(distractors) >= 3: break
                    if gd not in distractors and gd != ans:
                        distractors.append(gd)
                        
                if len(distractors) < 3:
                    continue
                    
                wrong_opts = random.sample(distractors, 3)
                options_list = [ans] + wrong_opts
                random.shuffle(options_list)
                
                letters = ["A", "B", "C", "D"]
                opts_dict = {letters[i]: options_list[i] for i in range(4)}
                correct_letter = letters[options_list.index(ans)]
                
                questions.append({
                    "text": f"According to Wikipedia ({title}): {q_text}",
                    "options": opts_dict,
                    "correct_option": correct_letter,
                    "difficulty": difficulty,
                    "source": "backend_generation"
                })
                
    return questions

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

    questions = fetch_from_opentdb(topic, difficulty, count)
    source = "opentdb" if questions else "local"

    if len(questions) < count:
        local = generate_local_questions(topic, difficulty, count - len(questions))
        questions.extend(local)
        if source == "opentdb" and local:
            source = "mixed"

    if len(questions) < count:
        wiki_questions = generate_wikipedia_questions(topic, difficulty, count - len(questions))
        questions.extend(wiki_questions)
        if source == "opentdb" and wiki_questions:
            source = "mixed"
        elif source == "local" and wiki_questions:
            source = "mixed"
        elif not questions and wiki_questions:
            source = "wikipedia"

    return {
        "topic": topic,
        "difficulty": difficulty,
        "count": len(questions),
        "source": source,
        "questions": questions,
    }
