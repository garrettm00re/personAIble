export function initializeChat() {
    document.getElementById('user-input').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            submitQuestion();
        }
    });
}

export async function submitQuestion() {
    const input = document.getElementById('user-input');
    const question = input.value.trim();
    console.log('Submitting question:', question);
    if (question) {
        addMessage(question, 'user');
        input.value = '';
        
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                addMessage(data.answer, 'system');
            } else {
                addMessage('Error: ' + data.error, 'system');
            }
        } catch (error) {
            addMessage('Error connecting to the server', 'system');
            console.error('Error:', error);
        }
    }
}

export function addMessage(text, type) {
    const qaContainer = document.getElementById('qa-container');
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    message.textContent = text;
    qaContainer.appendChild(message);
    qaContainer.scrollTop = qaContainer.scrollHeight;
}