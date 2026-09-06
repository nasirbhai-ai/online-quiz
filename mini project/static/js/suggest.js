/**
 * Topic Question Suggester — fetches and displays suggested MCQs.
 */
(function () {
    'use strict';

    const form = document.getElementById('suggestForm');
    const topicInput = document.getElementById('topicInput');
    const difficultySelect = document.getElementById('difficultySelect');
    const countInput = document.getElementById('countInput');
    const suggestBtn = document.getElementById('suggestBtn');
    const suggestStatus = document.getElementById('suggestStatus');
    const resultsEmpty = document.getElementById('resultsEmpty');
    const resultsList = document.getElementById('resultsList');
    const resultMeta = document.getElementById('resultMeta');
    const quizActionBar = document.getElementById('quizActionBar');
    const startTopicQuizBtn = document.getElementById('startTopicQuizBtn');

    let currentSuggestions = null;

    // Topic chip quick-select
    document.getElementById('topicChips')?.addEventListener('click', (e) => {
        const chip = e.target.closest('.topic-chip');
        if (!chip) return;
        topicInput.value = chip.dataset.topic;
        document.querySelectorAll('.topic-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
    });

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await fetchSuggestions();
    });

    async function fetchSuggestions() {
        const topic = topicInput.value.trim();
        if (!topic) return;

        suggestBtn.disabled = true;
        suggestBtn.textContent = 'Generating...';
        showStatus('Fetching question suggestions...', 'info');

        try {
            const response = await fetch('/api/suggest-questions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: topic,
                    difficulty: difficultySelect.value,
                    count: parseInt(countInput.value, 10) || 5
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showStatus(data.error || 'Failed to fetch suggestions.', 'danger');
                return;
            }

            currentSuggestions = data;
            renderResults(data);
            hideStatus();

            const sourceLabel = {
                opentdb: 'Open Trivia DB',
                local: 'Local Generator',
                mixed: 'Mixed Sources'
            };
            showStatus(
                `Loaded ${data.count} questions for "${data.topic}" (${sourceLabel[data.source] || data.source})`,
                'success'
            );
        } catch (err) {
            showStatus('Network error. Please try again.', 'danger');
        } finally {
            suggestBtn.disabled = false;
            suggestBtn.textContent = 'Suggest Questions';
        }
    }

    function renderResults(data) {
        resultsEmpty.hidden = true;
        resultsList.hidden = false;
        resultMeta.textContent = `${data.topic} · ${data.difficulty} · ${data.count} questions`;

        if (quizActionBar) quizActionBar.hidden = false;

        resultsList.innerHTML = '';

        data.questions.forEach((q, index) => {
            const card = document.createElement('div');
            card.className = 'suggested-question-card';

            const optionsHtml = Object.entries(q.options)
                .map(([letter, text]) => {
                    const isCorrect = letter === q.correct_option;
                    return `<li data-correct="${isCorrect}">
                        <span class="option-letter">${letter}</span> ${escapeHtml(text)}
                        ${isCorrect ? '<span class="correct-badge" style="display:none;">Correct</span>' : ''}
                    </li>`;
                })
                .join('');

            card.innerHTML = `
                <div class="sq-header">
                    <span class="sq-number">Q${index + 1}</span>
                    <span class="badge badge-${q.difficulty}">${q.difficulty}</span>
                    <span class="sq-source">${q.source || 'suggested'}</span>
                </div>
                <p class="sq-text">${escapeHtml(q.text)}</p>
                <ul class="sq-options">${optionsHtml}</ul>
                <div class="sq-actions" style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                    <button type="button" class="btn btn-outline btn-sm" onclick="const card = this.closest('.suggested-question-card'); card.querySelectorAll('[data-correct=\\'true\\']').forEach(el => { el.classList.add('correct-option'); el.querySelector('.correct-badge').style.display = 'inline-block'; }); this.remove();">
                        Show Answer
                    </button>
                    ${window.SUGGEST_CONFIG.isLoggedIn ? `
                        <button type="button" class="btn btn-outline btn-sm save-btn" data-index="${index}">
                            Save to Question Bank
                        </button>
                    ` : ''}
                </div>
            `;

            resultsList.appendChild(card);
        });

        // Attach save handlers
        resultsList.querySelectorAll('.save-btn').forEach(btn => {
            btn.addEventListener('click', () => saveQuestion(parseInt(btn.dataset.index, 10), btn));
        });
    }

    async function saveQuestion(index, btn) {
        if (!currentSuggestions) return;

        const q = currentSuggestions.questions[index];
        btn.disabled = true;
        btn.textContent = 'Saving...';

        try {
            const response = await fetch(window.SUGGEST_CONFIG.saveQuestionUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: currentSuggestions.topic,
                    text: q.text,
                    options: q.options,
                    correct_option: q.correct_option,
                    difficulty: q.difficulty
                })
            });

            const data = await response.json();

            if (response.ok) {
                btn.textContent = 'Saved ✓';
                btn.classList.add('saved');
            } else {
                btn.textContent = data.error || 'Failed';
                btn.disabled = false;
            }
        } catch (err) {
            btn.textContent = 'Error — Retry';
            btn.disabled = false;
        }
    }

    startTopicQuizBtn?.addEventListener('click', async () => {
        if (!currentSuggestions || !currentSuggestions.questions.length) return;

        startTopicQuizBtn.disabled = true;
        startTopicQuizBtn.textContent = 'Starting...';

        try {
            const response = await fetch(window.SUGGEST_CONFIG.startQuizUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: currentSuggestions.topic,
                    difficulty: currentSuggestions.difficulty,
                    questions: currentSuggestions.questions
                })
            });

            const data = await response.json();

            if (response.ok && data.redirect) {
                window.location.href = data.redirect;
            } else {
                alert(data.error || 'Could not start quiz.');
                startTopicQuizBtn.disabled = false;
                startTopicQuizBtn.textContent = 'Take Quiz with These Questions';
            }
        } catch (err) {
            alert('Network error. Please try again.');
            startTopicQuizBtn.disabled = false;
            startTopicQuizBtn.textContent = 'Take Quiz with These Questions';
        }
    });

    function showStatus(msg, type) {
        suggestStatus.hidden = false;
        suggestStatus.className = 'suggest-status alert alert-' + type;
        suggestStatus.textContent = msg;
    }

    function hideStatus() {
        // Keep success/info messages visible briefly
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
})();
