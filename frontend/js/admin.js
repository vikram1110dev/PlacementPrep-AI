document.addEventListener("DOMContentLoaded", function () {
    
    // Sidebar Toggle for Mobile
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    if(sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-open');
        });
    }

    Chart.defaults.font.family = "'Poppins', sans-serif";

    // Chart.js - Dashboard Revenue (if exists)
    const revCtx = document.getElementById('revenueChart');
    if (revCtx) {
        new Chart(revCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue ($)',
                    data: [12000, 19000, 15000, 22000, 30000, 28000],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16,185,129,0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    // Chart.js - Dashboard Users (if exists)
    const usersCtx = document.getElementById('usersChart');
    if (usersCtx) {
        new Chart(usersCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'New Users',
                    data: [400, 800, 600, 1200, 1500, 1100],
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    // Mock Action Buttons
    const actionBtns = document.querySelectorAll('.mock-action');
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.getAttribute('data-action');
            if(action === 'delete') {
                if(confirm("Are you sure you want to delete this record?")) {
                    this.closest('tr').remove();
                }
            } else if (action === 'suspend') {
                alert("User suspended.");
            } else {
                alert(action + " action triggered.");
            }
        });
    });

});
