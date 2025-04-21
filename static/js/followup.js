import { addMessage } from './chat.js';
import { submit } from './chat.js';

const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('uid');

let currentFollowupShown = false;  // Add this flag at the top of the file
let pollingActive = true;  // Add flag to control polling

export async function startFollowupPolling() {
    window.submit = submitFollowupAnswer;
    while (pollingActive) {  // Use flag instead of true
        try {
            const response = await fetch(`/api/check-followup/?uid=${userId}`);
            const data = await response.json();
            
            if (data.hasFollowup && !currentFollowupShown) {
                addMessage(data.question, 'system', true);
                // Store question for when we submit the answer
                window.currentFollowupQuestion = data.question;
                currentFollowupShown = true;  // Set flag after showing the message
            }
            
            await new Promise(r => setTimeout(r, 2000));
        } catch (error) {
            console.error('Polling error:', error);
        }
    }
    window.submit = submit;
}

export async function submitFollowupAnswer(answer) {
    try {
        const response = await fetch('/api/submit-followup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                answer,
                question: window.currentFollowupQuestion 
            })
        });
        if (!response.ok) {
            throw new Error('Failed to submit answer');
        }
        currentFollowupShown = false;  // Reset the flag after successful submission
    } catch (error) {
        console.error('Error submitting followup:', error);
    }
}

// Add cleanup function
export function stopFollowupPolling() {
    pollingActive = false;
}

// Add event listener for page unload
window.addEventListener('beforeunload', stopFollowupPolling);