document.addEventListener('DOMContentLoaded', () => {

    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const body = document.body;

    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') {
        body.classList.add('dark-mode');
        themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }

    themeToggleBtn.addEventListener('click', () => {
        body.classList.toggle('dark-mode');

        const isDarkMode = body.classList.contains('dark-mode');
        themeToggleBtn.innerHTML = isDarkMode ?
            '<i class="fas fa-sun"></i>' :
            '<i class="fas fa-moon"></i>';

        localStorage.setItem('darkMode', isDarkMode);
    });

    const enhanceAccessibility = () => {

        document.querySelectorAll('button:not([aria-label])').forEach(button => {
            if (!button.getAttribute('aria-label')) {
                const text = button.textContent.trim();
                if (text) {
                    button.setAttribute('aria-label', text);
                }
            }
        });

        document.querySelectorAll('a, button, input, select, [tabindex="0"]').forEach(el => {
            el.addEventListener('keyup', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    el.click();
                }
            });
        });
    };

    enhanceAccessibility();
});

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    if (!seconds) return '0:00';

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);

    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function trackEvent(category, action, label) {

    console.log(`Event tracked: ${category} - ${action} - ${label}`);

}