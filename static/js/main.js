import { initializeChat, submit } from './chat.js';
import { initializeNavigation, navigate } from './navigation.js';
import { saveChanges } from './dataManager.js';
import { submitFollowupAnswer } from './followup.js';

// This is our entry point - it initializes everything when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    initializeNavigation();
});

// Make necessary functions available to global scope for onclick handlers
window.submit = submit; // overriden in several places (i.e. onboarding)
window.submitFollowup = submitFollowupAnswer;
window.navigate = navigate;
window.saveChanges = saveChanges;