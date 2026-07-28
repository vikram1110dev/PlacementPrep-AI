/**
 * Dark / Light Mode Theme Manager
 */
class ThemeManager {
    static init() {
        // Check local storage for preference
        const savedTheme = localStorage.getItem('pp_theme');
        if (savedTheme) {
            this.setTheme(savedTheme);
        } else {
            // Default to light
            this.setTheme('light');
        }

        // Attach listener for dynamic loaded navbar
        document.addEventListener('click', (e) => {
            if(e.target.closest('#themeToggleBtn')) {
                this.toggleTheme();
            }
        });
    }

    static toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        this.setTheme(currentTheme);
    }

    static setTheme(theme) {
        if(theme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            localStorage.setItem('pp_theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
            localStorage.setItem('pp_theme', 'light');
        }
        this.updateIcon(theme);
    }

    static updateIcon(theme) {
        const btn = document.getElementById('themeToggleBtn');
        if(!btn) return;
        const icon = btn.querySelector('i');
        if(icon) {
            if(theme === 'dark') {
                icon.className = 'bi bi-sun';
            } else {
                icon.className = 'bi bi-moon';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
