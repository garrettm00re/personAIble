export function initializeChat() {
}

export async function submit() {
    const input = document.getElementById('user-input');
    const userInput = input.value.trim();
    const qaContainer = document.getElementById('qa-container');
    const lastMessage = qaContainer.lastElementChild;
    const isQuestion = !lastMessage || !lastMessage.classList.contains('system-message') || !lastMessage.classList.contains('follow-up');
    if (isQuestion) {
        console.log('Submitting question:', userInput);
        addMessage(userInput, 'user');
        input.value = '';
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: userInput })
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

    else {
        console.log('Submitting followup answer:', userInput);
        addMessage(userInput, 'user', true);
        if (window.pendingFollowUpCallback) {
            window.pendingFollowUpCallback(userInput);
        }
    }
    input.value = '';
}

export function addMessage(text, type, isFollowUp = false) {
    // type: user, system
    // need a way to denote followup questions and followup answers
    // need a way to return the followup question to the backend (and then the model)
    console.log('addMessage. text ===', text)
    const qaContainer = document.getElementById('qa-container');
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    
    if (isFollowUp) {
        message.className += ' follow-up';
        // Add a visual indicator for follow-up messages
        const followUpIndicator = document.createElement('span');
        followUpIndicator.className = 'follow-up-indicator';
        followUpIndicator.textContent = '↳';
        message.prepend(followUpIndicator);
    }
    
    const textSpan = document.createElement('span');
    textSpan.textContent = text;
    message.appendChild(textSpan);
    
    qaContainer.appendChild(message);

    console.log('autoscrolling') // not working at the moment
    requestAnimationFrame(() => {
        qaContainer.scrollTop = qaContainer.scrollHeight;
    });
}

function initializeTextarea() {
    const textarea = document.getElementById('user-input');
    
    function autoResize() {
        textarea.style.height = 'auto';  // Reset height
        const newHeight = Math.min(textarea.scrollHeight, 200);  // Cap at max-height
        textarea.style.height = newHeight + 'px';
        
        // Update container height
        const container = document.querySelector('.input-container');
        container.style.height = (newHeight) + 'px';  // Add padding
    }

    // Call on input changes
    textarea.addEventListener('input', autoResize);
    
    // Initial size
    autoResize();
}

// Add to your initialization code
document.addEventListener('DOMContentLoaded', initializeTextarea);
