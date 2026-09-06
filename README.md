# QuizMaster — Online Quiz Platform

A full-featured online MCQ quiz platform built with **Flask**, **SQLite**, and a responsive web UI.

## Features

- User registration and login (Flask-Login)
- MCQ quizzes with multiple categories and difficulty levels (Easy, Medium, Hard)
- **Topic Question Suggester** — choose any topic and get new MCQ questions via API
- 30-second timer per question with auto-advance
- Automatic scoring after quiz submission
- Global leaderboard with top scores and recent activity
- Responsive dark-themed UI (HTML, CSS, JavaScript)
- SQLite database with SQLAlchemy ORM

## API Endpoints

### `GET /api/topics`
Returns suggested topics and existing categories.

### `POST /api/suggest-questions`
Suggest new MCQ questions for a user-chosen topic.

```json
{
  "topic": "Science",
  "difficulty": "medium",
  "count": 5
}
```

Response includes questions with options, correct answer, and source (`opentdb`, `local`, or `mixed`).

### `POST /api/save-question` (login required)
Save a suggested question to the database.

```json
{
  "topic": "Space",
  "text": "What is the largest planet?",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "correct_option": "B",
  "difficulty": "easy"
}
```

## Topic Suggester Page

Visit **/quiz/suggest** to:
1. Choose a topic (preset chips or custom text)
2. Select difficulty and question count
3. Click **Suggest Questions** to fetch MCQs
4. **Save** individual questions to the question bank
5. **Take Quiz** with the suggested questions

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database

```bash
python seed.py
```

This creates 4 categories (Science, History, Geography, Technology) with 10 questions each across all difficulty levels.

### 3. Run the server

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
├── app/
│   ├── __init__.py       # App factory
│   ├── models.py         # User, Category, Question, Score models
│   ├── extensions.py     # Shared Flask extensions
│   ├── utils.py          # Validation & helper functions
│   └── routes/
│       ├── auth.py       # Register, login, logout
│       ├── api.py        # Question suggestion API
│       ├── main.py       # Home, leaderboard
│       └── quiz.py       # Quiz list, take, submit, suggest page
│   └── services/
│       └── question_suggester.py  # Topic-based question generation
├── templates/            # Jinja2 HTML templates
├── static/
│   ├── css/style.css     # Responsive styles
│   └── js/quiz.js        # Timer & quiz logic
├── config.py             # App configuration
├── seed.py               # Database seeder
├── run.py                # Entry point
└── requirements.txt
```

## Configuration

Edit `config.py` to change:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECONDS_PER_QUESTION` | 30 | Timer duration per question |
| `QUESTIONS_PER_QUIZ` | 5 | Questions per quiz attempt |

For PostgreSQL, set the `DATABASE_URL` environment variable:

```bash
set DATABASE_URL=postgresql://user:pass@localhost/quizdb
```

## Usage

1. **Register** a new account at `/auth/register`
2. **Browse quizzes** at `/quiz/`
3. **Pick** a category and difficulty level
4. **Answer** timed questions (30s each)
5. **View results** and check the **leaderboard**

## Tech Stack

- Python 3.10+
- Flask 3.x
- Flask-Login, Flask-SQLAlchemy
- SQLite (default) / PostgreSQL
- HTML5, CSS3, Vanilla JavaScript
