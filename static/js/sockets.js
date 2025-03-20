import { addMessage } from './chat.js';

console.log("IMPORTED")
const socket = io();

// Define at the top level of sockets.js, outside any function
window.pendingFollowUpCallback = null;

// Connection status logs
socket.on('connect', () => {
    console.log('Socket.IO Connected!');
});

socket.on('connect_error', (error) => {
    console.log('Socket.IO Connection Error:', error);
});

socket.on('disconnect', (reason) => {
    console.log('Socket.IO Disconnected:', reason);
});

socket.on('ask_followup', (data) => {
    console.log('Received ask_followup event:', data);

    // integration plan:
    // addMessage(system question) (display the system question to the user)
    // when the user answers, addMessage(user answer) then collect their answer and return it here
    // continue with this function
    console.log("adding message (system question)")
    addMessage(data.question, 'system', true); // true for followup
    
    window.pendingFollowUpCallback = (answer) => { // this is a callback function that will be called (in chat.js/submit) when the user provides an answer
        console.log('User provided answer:', answer);
        socket.emit('followup_response', { // send the answer to the backend
            'answer': answer,
        });
    };
});

// Export socket if needed elsewhere
export { socket };