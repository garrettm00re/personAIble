import { addMessage } from './chat.js';

const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('uid');

async function startFollowupPolling() {
    while (true) {
        try {
            const response = await fetch(`/api/check-followup/?uid=${userId}`); // 
            const data = await response.json();
            
            if (data.hasFollowup) {
                addMessage(data.question, 'system', true);
                // Store question for when we submit the answer
                window.currentFollowupQuestion = data.question;
            }
            
            await new Promise(r => setTimeout(r, 2000));
        } catch (error) {
            console.error('Polling error:', error);
        }
    }
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
    } catch (error) {
        console.error('Error submitting followup:', error);
    }
}

// Start polling when imported
startFollowupPolling();