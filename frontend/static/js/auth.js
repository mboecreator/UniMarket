// Simple authentication page enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.messages .alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Add click to dismiss functionality for messages
    messages.forEach(message => {
        message.style.cursor = 'pointer';
        message.addEventListener('click', () => {
            message.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => {
                message.remove();
            }, 300);
        });
    });
});

// Add slideOutRight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);