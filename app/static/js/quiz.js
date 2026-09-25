/**
 * QuizMaster — Interactive quiz engine with per-question timer.
 */
(function () {
    'use strict';

    const dataEl = document.getElementById('quizData');
    if (!dataEl) return;

    const quizData = JSON.parse(dataEl.textContent);
    const questions = quizData.questions;
    const secondsPerQuestion = quizData.secondsPerQuestion;

    let currentIndex = 0;
    let answers = {};
    let timeRemaining = secondsPerQuestion;
    let timerInterval = null;
    let totalTimeTaken = 0;
    let quizStartTime = Date.now();

    const container = document.getElementById('quizContainer');
    const timerEl = document.getElementById('timer');
    const currentQEl = document.getElementById('currentQuestion');
    const progressFill = document.getElementById('progressFill');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    /** Build question DOM elements */
    function renderQuestions() {
        container.innerHTML = '';
        questions.forEach((q, index) => {
            const card = document.createElement('div');
            card.className = 'question-card' + (index === 0 ? ' active' : '');
            card.dataset.index = index;

            const textEl = document.createElement('p');
            textEl.className = 'question-text';
            textEl.textContent = q.text;
            card.appendChild(textEl);

            const optionsList = document.createElement('div');
            optionsList.className = 'options-list';

            Object.entries(q.options).forEach(([letter, text]) => {
                const option = document.createElement('div');
                option.className = 'option-item';
                option.dataset.questionId = q.id;
                option.dataset.letter = letter;

                option.innerHTML =
                    '<span class="option-letter">' + letter + '</span>' +
                    '<span class="option-text">' + escapeHtml(text) + '</span>';

                option.addEventListener('click', () => selectOption(q.id, letter, option));
                optionsList.appendChild(option);
            });

            card.appendChild(optionsList);
            container.appendChild(card);
        });

        updateProgress();
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /** Handle option selection */
    function selectOption(questionId, letter, optionEl) {
        const card = optionEl.closest('.question-card');
        card.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
        optionEl.classList.add('selected');
        answers[String(questionId)] = letter;
    }

    /** Show question at given index */
    function showQuestion(index) {
        document.querySelectorAll('.question-card').forEach((card, i) => {
            card.classList.toggle('active', i === index);
        });

        currentIndex = index;
        currentQEl.textContent = index + 1;
        prevBtn.disabled = index === 0;
        nextBtn.style.display = index < questions.length - 1 ? 'inline-flex' : 'none';
        submitBtn.style.display = index === questions.length - 1 ? 'inline-flex' : 'none';

        // Restore selected state
        const q = questions[index];
        const saved = answers[String(q.id)];
        if (saved) {
            const card = document.querySelector('.question-card[data-index="' + index + '"]');
            card.querySelectorAll('.option-item').forEach(el => {
                el.classList.toggle('selected', el.dataset.letter === saved);
            });
        }

        resetTimer();
        updateProgress();
    }

    function updateProgress() {
        const pct = ((currentIndex + 1) / questions.length) * 100;
        progressFill.style.width = pct + '%';
    }

    /** Timer logic — 30 seconds per question */
    function resetTimer() {
        clearInterval(timerInterval);
        timeRemaining = secondsPerQuestion;
        updateTimerDisplay();

        timerInterval = setInterval(() => {
            timeRemaining--;
            updateTimerDisplay();

            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                autoAdvance();
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        timerEl.textContent = timeRemaining;
        timerEl.classList.remove('warning', 'danger');

        if (timeRemaining <= 5) {
            timerEl.classList.add('danger');
        } else if (timeRemaining <= 10) {
            timerEl.classList.add('warning');
        }
    }

    /** Auto-advance when timer expires */
    function autoAdvance() {
        totalTimeTaken += secondsPerQuestion;

        if (currentIndex < questions.length - 1) {
            showQuestion(currentIndex + 1);
        } else {
            submitQuiz();
        }
    }

    /** Submit answers to server */
    async function submitQuiz() {
        clearInterval(timerInterval);
        totalTimeTaken = Math.round((Date.now() - quizStartTime) / 1000);

        prevBtn.disabled = true;
        nextBtn.disabled = true;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            const response = await fetch('/quiz/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    answers: answers,
                    time_taken: totalTimeTaken
                })
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.error || 'Submission failed.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Quiz';
                return;
            }
            
            // Save detailed results for the result page
            if (result.results) {
                sessionStorage.setItem('quizResults', JSON.stringify(result.results));
            }

            window.location.href = result.redirect;
        } catch (err) {
            alert('Network error. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Quiz';
        }
    }

    // Event listeners
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            clearInterval(timerInterval);
            showQuestion(currentIndex - 1);
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentIndex < questions.length - 1) {
            clearInterval(timerInterval);
            showQuestion(currentIndex + 1);
        }
    });

    submitBtn.addEventListener('click', submitQuiz);

    // Initialize
    renderQuestions();
    showQuestion(0);
})();
