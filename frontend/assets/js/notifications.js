/**
 * Global Toast Notifications System
 */
class Notifications {
    
    /**
     * Show a toast message
     * @param {string} type 'success', 'error', 'warning', 'info'
     * @param {string} message The message to display
     */
    static show(type, message) {
        const container = document.getElementById('toastWrapper');
        if (!container) return; // Toast component not loaded yet

        const id = 'toast-' + Date.now();
        let icon = 'bi-info-circle';
        let bgClass = 'bg-info text-white';

        switch(type) {
            case 'success': icon = 'bi-check-circle-fill'; bgClass = 'bg-success text-white'; break;
            case 'error': icon = 'bi-x-circle-fill'; bgClass = 'bg-danger text-white'; break;
            case 'warning': icon = 'bi-exclamation-triangle-fill'; bgClass = 'bg-warning text-dark'; break;
        }

        const toastHTML = `
            <div id="${id}" class="toast align-items-center ${bgClass} border-0 mb-2 toast-slide-in" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center gap-2">
                        <i class="bi ${icon}"></i>
                        <span class="fw-medium">${message}</span>
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', toastHTML);
        
        // Initialize bootstrap toast
        const toastEl = document.getElementById(id);
        const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
        bsToast.show();

        // Cleanup after hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
}

window.showToast = Notifications.show;
