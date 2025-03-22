let onboardingQuestions = [];

async function loadOnboardingQuestions() {
    try {
        const response = await fetch('/static/onboardingQuestions.txt');
        if (!response.ok) {
            throw new Error('Failed to load onboarding questions');
        }
        const text = await response.text();
        onboardingQuestions = text.split('\n').filter(question => question.trim());
    } catch (error) {
        console.error('Error loading onboarding questions:', error);
    }
}

let currentQuestionIndex = 0;
let userName = "";
let userFirstName = "";
let onboardingDelay = 660;
// Add random variation of +/- 200ms to the base delay
let maxVariation = 260;
let getRandomDelay = () => onboardingDelay + (Math.random() * maxVariation - maxVariation/2);

export async function initializeOnboarding() {
    await loadOnboardingQuestions();

    // Show the first question
    let individualMessages = onboardingQuestions[0].split('.');
    for (let i = 0; i < individualMessages.length; i++) {
        setTimeout(() => {
            addMessage(individualMessages[i], 'system');
        }, getRandomDelay() * i); //setTimeout is non-blocking
    }

    // Override the submit function defined in chat.js
    window.submit = async function() {
        
        const input = document.getElementById('user-input');
        const userInput = input.value.trim();
        if (!userInput) return;

        if (currentQuestionIndex === 0) {
            userName = userInput;
            userFirstName = userName.split(' ')[0];
        }

        // Add user's answer
        addMessage(userInput, 'user');
        input.value = '';

        storeAnswer(currentQuestionIndex, userInput);

        currentQuestionIndex++;
        
        // If there are more questions, show the next one
        if (currentQuestionIndex < onboardingQuestions.length) {
            let question = onboardingQuestions[currentQuestionIndex];
            question = question.replace('{name}', userFirstName); // replace {name} with the user's name
            setTimeout(() => {
                addMessage(question, 'system');
            }, onboardingDelay); // Small delay for better UX
        } else {
            // Show completion message or handle end of onboarding
            setTimeout(() => {
                addMessage("Great, thank you " + userFirstName + "! Let's get started!", 'system');
                // Option 2: Wait for success (if you want to ensure the POST worked)
                setTimeout(async () => {
                    try {
                        const response = await fetch('/onboarding/submit', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                        if (response.ok) {
                            window.location.href = '/app';
                        }
                    } catch (error) {
                        console.error('Error:', error);
                    }
                }, onboardingDelay);
            }, onboardingDelay);
        }
    };
}

async function storeAnswer(questionIndex, userAnswer) {
    try {
        // This POST request happens in the background
        const response = await fetch('/api/onboarding/store', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: onboardingQuestions[questionIndex],
                answer: userAnswer,
            })
        });

        // Even after the POST completes, we stay on the same page
    } catch (error) {
        console.error('Error storing onboarding answer:', error);
    }
}

document.addEventListener('DOMContentLoaded', initializeOnboarding);

// Import the addMessage function from chat.js to maintain consistent message display
import { addMessage } from './chat.js';