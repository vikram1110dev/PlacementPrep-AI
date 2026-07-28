/**
 * Navigation & Component Injection Loader
 */
class Navigation {
    static init() {
        this.loadComponents();
        this.initSidebarToggle();
        this.initSearch();
    }

    /**
     * Loads HTML components dynamically into placeholders.
     */
    static loadComponents() {
        const components = [
            { id: 'sidebar-container', url: '../components/sidebar.html' },
            { id: 'navbar-container', url: '../components/navbar.html' },
            { id: 'footer-container', url: '../components/footer.html' },
            { id: 'toast-container', url: '../components/toast.html' }
        ];

        components.forEach(async (comp) => {
            const el = document.getElementById(comp.id);
            if (el) {
                try {
                    const response = await fetch(comp.url);
                    if (response.ok) {
                        const html = await response.text();
                        el.innerHTML = html;
                        this.afterComponentLoad(comp.id);
                    }
                } catch (error) {
                    console.error(`Failed to load component ${comp.url}:`, error);
                }
            }
        });
    }

    /**
     * Re-bind events after a component loads via innerHTML.
     */
    static afterComponentLoad(id) {
        if (id === 'sidebar-container' || id === 'navbar-container') {
            this.initSidebarToggle();
            
            // Mark active nav link based on current path
            const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';
            const links = document.querySelectorAll('.sidebar-link');
            links.forEach(link => {
                if(link.getAttribute('href') === currentPath) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }
    }

    static initSidebarToggle() {
        const toggleBtn = document.getElementById('sidebarToggleBtn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');

        if (toggleBtn && sidebar && overlay) {
            // Remove old listeners to prevent duplicates if called twice
            const newToggleBtn = toggleBtn.cloneNode(true);
            toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);
            
            newToggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
                overlay.classList.toggle('show');
            });
            
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('open');
                overlay.classList.remove('show');
            });
        }
    }

    static initSearch() {
        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                // Autocomplete/search logic placeholder
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => Navigation.init());
