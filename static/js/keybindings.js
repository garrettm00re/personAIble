document.addEventListener('keydown', (event) => {
    if (event.target.id === 'user-input' && event.key === 'Enter') {
        event.preventDefault();
        submit();
    }
});

// should be able to use shift + enter to add a new line

