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
        fetchSuggestions();
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

            if (!window.SUGGEST_CONFIG.isLoggedIn) {
                showStatus('You must log in to start a quiz.', 'danger');
                return;
            }

            currentSuggestions = data;
            
            showStatus('Starting quiz...', 'success');
            await startQuizAutomatically(data);

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

    async function startQuizAutomatically(data) {
        if (!data || !data.questions || !data.questions.length) return;

        try {
            const response = await fetch(window.SUGGEST_CONFIG.startQuizUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: data.topic,
                    difficulty: data.difficulty,
                    questions: data.questions
                })
            });

            const result = await response.json();

            if (response.ok && result.redirect) {
                window.location.href = result.redirect;
            } else {
                showStatus(result.error || 'Could not start quiz.', 'danger');
            }
        } catch (err) {
            showStatus('Network error. Please try again.', 'danger');
        }
    }

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
