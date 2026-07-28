/**
 * Global Page Loader & Skeleton Manager
 */
class Loader {
    static init() {
        // Remove full screen loader once page is ready
        window.addEventListener('load', () => {
            const pageLoader = document.getElementById('pageLoader');
            if (pageLoader) {
                pageLoader.classList.add('fade-out');
                setTimeout(() => pageLoader.remove(), 500);
            }
        });
    }

    /**
     * Replaces an element's HTML with skeleton loader
     */
    static showSkeleton(elementId, type = 'card') {
        const el = document.getElementById(elementId);
        if(!el) return;

        let html = '';
        if (type === 'card') {
            html = `
                <div class="skeleton skeleton-block mb-3"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text skeleton-text-short"></div>
            `;
        }
        
        // Store original content
        el.setAttribute('data-original-html', el.innerHTML);
        el.innerHTML = html;
    }

    /**
     * Restores original HTML
     */
    static hideSkeleton(elementId) {
        const el = document.getElementById(elementId);
        if(!el) return;
        
        const originalHTML = el.getAttribute('data-original-html');
        if(originalHTML) {
            el.innerHTML = originalHTML;
        }
    }
}

Loader.init();
