import { addMessage } from './chat.js';

console.log("IMPORTED")
const socket = io();



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
    const answer = prompt(data.question);
    console.log('User provided answer:', answer);
    
    socket.emit('followup_response', {
        'answer': answer,
    });
});

// Export socket if needed elsewhere
export { socket };