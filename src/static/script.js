const userInput = document.getElementById('user-input');
const predictionOverlay = document.getElementById('prediction-overlay');

let currentPrediction = '';
let lastValue = '';

// Smoother auto-resize for the textarea
function autoResize() {
    // We only recalculate if the scrollHeight has changed relative to current height
    // This avoids resetting the height to 'auto' on every stroke, which is choppy.
    const currentScrollHeight = userInput.scrollHeight;
    if (Math.abs(userInput.offsetHeight - currentScrollHeight) > 10) {
        userInput.style.height = currentScrollHeight + 'px';
        predictionOverlay.height = currentScrollHeight + 'px';
    }
}

userInput.addEventListener('input', async (e) => {
    const text = e.target.value;
    
    // Only resize if content changed significantly
    if (text !== lastValue) {
        autoResize();
        lastValue = text;
    }

    if (!text.trim()) {
        predictionOverlay.textContent = '';
        currentPrediction = '';
        return;
    }

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });

        const data = await response.json();
        const fullPrediction = data.prediction;

        if (fullPrediction && (fullPrediction.toLowerCase().startsWith(text.toLowerCase()) || fullPrediction.includes("{P}"))) {
            let ghostText = '';
            if (fullPrediction.toLowerCase().startsWith(text.toLowerCase())) {
                ghostText = fullPrediction.substring(text.length);
            } else {
                ghostText = ` -> ${fullPrediction}`;
            }
            
            // Re-render only if the prediction changed
            if (currentPrediction !== fullPrediction || text !== lastValue) {
                predictionOverlay.innerHTML = `<span style="color: transparent;">${text}</span>${ghostText}`;
                currentPrediction = fullPrediction;
            }
        } else {
            predictionOverlay.textContent = '';
            currentPrediction = '';
        }

    } catch (err) {
        console.error('Prediction error:', err);
    }
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' || (e.key === 'ArrowRight' && userInput.selectionStart === userInput.value.length)) {
        if (currentPrediction && !currentPrediction.includes("->")) {
            e.preventDefault();
            userInput.value = currentPrediction;
            predictionOverlay.textContent = '';
            lastValue = currentPrediction;
            autoResize();
        }
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
