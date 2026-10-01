import requests
import re
import random

def generate_wikipedia_questions(topic, difficulty, count):
    # 1. Search for the topic to handle spelling mistakes
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={topic}&utf8=&format=json&srlimit=1"
    try:
        search_res = requests.get(search_url, timeout=5).json()
        search_results = search_res.get("query", {}).get("search", [])
        if not search_results:
            return []
        title = search_results[0]["title"]
    except Exception as e:
        return []

    # 2. Get the extract
    extract_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exlimit=1&titles={title}&explaintext=1&format=json"
    try:
        extract_res = requests.get(extract_url, timeout=5).json()
        pages = extract_res.get("query", {}).get("pages", {})
        page = list(pages.values())[0]
        text = page.get("extract", "")
        if not text:
            return []
    except Exception as e:
        return []

    # 3. Clean and split into sentences
    text = re.sub(r'==.*?==', '', text) # Remove headers
    text = re.sub(r'\n+', ' ', text)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.split()) > 5 and len(s.split()) < 30]

    # 4. Generate MCQs
    questions = []
    # Collect all possible words for distractors
    all_words = []
    for s in sentences:
        words = [w for w in re.findall(r'\b[A-Z][a-z]+\b|\b\d+\b', s) if len(w) > 3]
        all_words.extend(words)
    all_words = list(set(all_words))

    for s in sentences:
        if len(questions) >= count:
            break
            
        # Find candidates: Capitalized words (not first word) or numbers
        words = s.split()
        candidates = []
        for i, w in enumerate(words[1:]): # Skip first word
            clean_w = re.sub(r'[^\w]', '', w)
            if (clean_w.istitle() and clean_w.isalpha() and len(clean_w) > 3) or (clean_w.isdigit() and len(clean_w) >= 2):
                candidates.append((i+1, clean_w))
                
        if candidates:
            # Pick one candidate
            idx, ans = random.choice(candidates)
            
            # Create question
            q_words = words[:]
            q_words[idx] = "_____"
            q_text = " ".join(q_words)
            
            # Generate options
            distractors = [w for w in all_words if w != ans and (w.isdigit() == ans.isdigit())]
            if len(distractors) < 3:
                # Fallback distractors
                distractors.extend(["None of the above", "All of the above", "Unknown", "Not specified", "Various", "Multiple", "One", "Two", "Three"])
            
            wrong_opts = random.sample(distractors, 3)
            options_list = [ans] + wrong_opts
            random.shuffle(options_list)
            
            opts_dict = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
            correct_letter = [k for k, v in opts_dict.items() if v == ans][0]
            
            questions.append({
                "text": f"According to Wikipedia ({title}): " + q_text,
                "options": opts_dict,
                "correct_option": correct_letter,
                "difficulty": difficulty,
                "source": "wikipedia_fallback"
            })
            
    return questions

if __name__ == "__main__":
    qs = generate_wikipedia_questions("Spiderman", "medium", 5)
    for q in qs:
        print(q['text'])
        print(q['options'])
        print("Correct:", q['correct_option'])
        print()
