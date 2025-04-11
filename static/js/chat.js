export function initializeChat() {
}

export async function submit() {
    const input = document.getElementById('user-input');
    const userInput = input.value.trim();
    const qaContainer = document.getElementById('qa-container');
    const lastMessage = qaContainer.lastElementChild;
    const isQuestion = !lastMessage || !lastMessage.classList.contains('system-message') || !lastMessage.classList.contains('follow-up');
    // reset size of input container
    const inputContainer = document.getElementById("user-input-container")
    inputContainer.style.height = `40px`;
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
    console.log("Initializing textarea");
    const textarea = document.getElementById('user-input');
    const container = document.querySelector('.input-container');
    function autoResize() {
        console.log("AUTO RESIZING TEXT INPUT")
        container.style.height = 'auto';
        // Get the input bar's height (includes textarea and button)
        const userInputHeight = textarea.scrollHeight; // 5 accounts for border
        const maxHeight = window.innerHeight * 0.4; // 40vh maximum (in pixels)
        const newHeight = Math.min(userInputHeight, maxHeight); // Add padding
        container.style.height = `${newHeight}px`;
    }
    // Call on input changes
    textarea.addEventListener('input', autoResize);
    
    // Initial size
    autoResize();
}

// Make sure we're calling the initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM Content Loaded");
    initializeTextarea();
});
