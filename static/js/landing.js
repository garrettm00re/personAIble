// Smooth scroll for navigation
document.addEventListener('DOMContentLoaded', () => {
    // Optional: Add animations for elements as they scroll into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    });

    // Observe all animated elements
    document.querySelectorAll('.animate-on-scroll').forEach((el) => {
        observer.observe(el);
    });

    // Optional: Add any interactive demos or animations
    initializeDemo();
});

function initializeDemo() {
    // Add any demo animations or interactive features
    const demoContainer = document.querySelector('.demo-animation');
    if (!demoContainer) return;

    // Example: Simple typing animation
    const text = "Hello! How can I help you today?";
    let index = 0;

    function typeText() {
        if (index < text.length) {
            demoContainer.textContent += text.charAt(index);
            index++;
            setTimeout(typeText, 100);
        }
    }

    typeText();
}