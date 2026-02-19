/**
 * theme.js
 * Initializes and manages light/dark mode.
 * Included early in <head> to avoid Flash of Unstyled Content (FOUC).
 */

(function () {
    function getTheme() {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }

    const theme = getTheme();
    if (theme === 'light') {
        document.documentElement.classList.add('light-theme'); // Use on document element or body
    }

    // Since this runs in head, document.body might not be ready. We set a class on html.
    // So we need to ensure the CSS uses :root.light-theme or :root.light-theme.
    // Wait, let's just use html.light-theme for safety or set it when body is available.

    // Actually, setting on documentElement is safer here.
    if (theme === 'light') {
        document.documentElement.classList.add('light-theme');
    }

    window.addEventListener('DOMContentLoaded', () => {
        // Also apply to body to be safe, since our CSS used :root.light-theme
        if (theme === 'light') {
            document.body.classList.add('light-theme');
        }

        const toggleBtn = document.getElementById('theme-toggle');
        const iconMoon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
        const iconSun = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';

        function updateIcon(currentTheme) {
            if (toggleBtn) {
                toggleBtn.innerHTML = currentTheme === 'light' ? iconMoon : iconSun;
                toggleBtn.setAttribute('aria-label', currentTheme === 'light' ? 'Mode sombre' : 'Mode clair');
            }
        }

        updateIcon(theme);

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';

                if (newTheme === 'light') {
                    document.body.classList.add('light-theme');
                    document.documentElement.classList.add('light-theme');
                } else {
                    document.body.classList.remove('light-theme');
                    document.documentElement.classList.remove('light-theme');
                }

                localStorage.setItem('theme', newTheme);
                updateIcon(newTheme);
            });
        }
    });
})();
