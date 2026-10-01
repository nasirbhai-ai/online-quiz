import re

with open("app/services/question_suggester.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the API fetching bug
content = content.replace('"amount": min(count * 2, 30)', '"amount": count')

cricket_questions = """    "cricket": [
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
    ],"""

# Replace the existing cricket block
pattern = r'    "cricket": \[.*?    \],'
content = re.sub(pattern, cricket_questions, content, flags=re.DOTALL)

with open("app/services/question_suggester.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated question_suggester.py successfully.")
