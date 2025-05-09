import { initializeChat, submit } from './chat.js';
import { initializeNavigation, navigate } from './navigation.js';
import { saveChanges } from './dataManager.js';

// This is our entry point - it initializes everything when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    initializeNavigation();
});

// Make necessary functions available to global scope for onclick handlers
window.submit = submit;
window.navigate = navigate;
window.saveChanges = saveChanges;