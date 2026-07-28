document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Toggle Sidebar on mobile
    if (sidebarToggleBtn && sidebar && sidebarOverlay) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.add('show');
            sidebarOverlay.classList.add('show');
        });

        // Close sidebar when clicking outside (on overlay)
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }

    // Set active class on sidebar links
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Check if link navigates away, if so let it happen.
            // For demo purposes, we'll update UI visually.
            
            // Remove active from all
            sidebarLinks.forEach(l => l.classList.remove('active'));
            
            // Add active to clicked unless it's a logout link
            if(!this.classList.contains('text-danger')) {
                this.classList.add('active');
            }
            
            // On mobile, close sidebar after clicking a link
            if(window.innerWidth < 992) {
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
            }
        });
    });

    // Task Checkbox interaction
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskText = this.nextElementSibling.querySelector('h6');
            const smallText = this.nextElementSibling.querySelector('small');
            
            if (this.checked) {
                taskText.classList.add('text-decoration-line-through', 'text-muted');
                smallText.dataset.original = smallText.innerHTML; // Store original html
                smallText.innerHTML = 'Completed';
            } else {
                taskText.classList.remove('text-decoration-line-through', 'text-muted');
                if (smallText.dataset.original) {
                    smallText.innerHTML = smallText.dataset.original; // Restore original html
                }
            }
        });
    });

    // Mock Dark Mode Toggle
    const darkModeBtn = document.querySelector('.nav-action-btn[title="Toggle Dark Mode"]');
    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', function() {
            // For now just toggle icon to show interaction
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-moon')) {
                icon.classList.replace('bi-moon', 'bi-sun');
                alert('Dark mode toggle clicked! (UI Only)');
            } else {
                icon.classList.replace('bi-sun', 'bi-moon');
            }
        });
    }
});
