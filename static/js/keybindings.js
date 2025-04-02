const textarea = document.getElementById('user-input');

textarea.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        submit();
    }
});

// should be able to use shift + enter to add a new line

