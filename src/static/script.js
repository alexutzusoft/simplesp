const userInput = document.getElementById('user-input');
const predictionOverlay = document.getElementById('prediction-overlay');
const predictionResults = document.getElementById('prediction-results');
const limitSelector = document.getElementById('limit-selector');

let currentPredictions = [];
let lastValue = '';
let currentLimit = 1;

// Smoother auto-resize for the textarea
function autoResize() {
    const currentScrollHeight = userInput.scrollHeight;
    if (Math.abs(userInput.offsetHeight - currentScrollHeight) > 10) {
        userInput.style.height = currentScrollHeight + 'px';
        predictionOverlay.style.height = currentScrollHeight + 'px';
    }
}

function selectPrediction(text) {
    userInput.value = text;
    predictionOverlay.textContent = '';
    predictionResults.innerHTML = '';
    currentPredictions = [];
    lastValue = text;
    autoResize();
    userInput.focus();
}

userInput.addEventListener('input', async (e) => {
    const text = e.target.value;
    
    if (text !== lastValue) {
        autoResize();
        lastValue = text;
    }

    if (!text.trim()) {
        predictionOverlay.textContent = '';
        predictionResults.innerHTML = '';
        currentPredictions = [];
        return;
    }

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, limit: currentLimit }),
        });

        const data = await response.json();
        currentPredictions = data.predictions || [];

        // 1. Ghost text for the first prediction
        const firstMatch = currentPredictions[0];
        if (firstMatch && (firstMatch.toLowerCase().startsWith(text.toLowerCase()) || firstMatch.includes("{P}"))) {
            let ghostText = '';
            if (firstMatch.toLowerCase().startsWith(text.toLowerCase())) {
                ghostText = firstMatch.substring(text.length);
            } else {
                ghostText = ` -> ${firstMatch}`;
            }
            predictionOverlay.innerHTML = `<span style="color: transparent;">${text}</span>${ghostText}`;
        } else {
            predictionOverlay.textContent = '';
        }

        // 2. Render all results in the list
        predictionResults.innerHTML = '';
        if (currentLimit > 1) {
            currentPredictions.forEach((pred, index) => {
                const card = document.createElement('div');
                card.className = 'result-card';
                const textEl = document.createElement('div');
                textEl.className = 'result-text';
                textEl.textContent = pred;
                card.appendChild(textEl);
                card.onclick = () => selectPrediction(pred);
                predictionResults.appendChild(card);
            });
        }

    } catch (err) {
        console.error('Prediction error:', err);
    }
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' || (e.key === 'ArrowRight' && userInput.selectionStart === userInput.value.length)) {
        if (currentPredictions.length > 0) {
            const firstMatch = currentPredictions[0];
            if (!firstMatch.includes("->")) {
                e.preventDefault();
                selectPrediction(firstMatch);
            }
        }
    }
});

// Limit buttons handling
limitSelector.addEventListener('click', (e) => {
    if (e.target.classList.contains('limit-btn')) {
        document.querySelectorAll('.limit-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        currentLimit = parseInt(e.target.dataset.limit);
        
        // Re-trigger prediction
        userInput.dispatchEvent(new Event('input'));
    }
});

// Fetch and update status stats
async function updateStatus() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        document.getElementById('status-text').textContent = `SimpleSP • ${data.sentences} sentences • ${data.files} files`;
    } catch (err) {
        document.getElementById('status-text').textContent = `SimpleSP • Active`;
    }
}

// Initial resize and status fetch
window.addEventListener('load', () => {
    autoResize();
    updateStatus();
});
