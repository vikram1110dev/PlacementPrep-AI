document.addEventListener("DOMContentLoaded", function () {

    // Common Chart Options
    Chart.defaults.font.family = "'Poppins', sans-serif";
    Chart.defaults.color = '#64748b';
    
    // 1. Line Chart - Daily Learning Hours
    const ctxLearning = document.getElementById('learningHoursChart').getContext('2d');
    new Chart(ctxLearning, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Study Hours',
                data: [2, 3.5, 2.5, 4, 3, 5.5, 4.5],
                borderColor: '#2563EB',
                backgroundColor: 'rgba(37,99,235,0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#2563EB',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
                x: { grid: { display: false } }
            }
        }
    });

    // 2. Bar Chart - Problems Solved Per Week (Now dynamically fetched)
    const ctxProblems = document.getElementById('problemsSolvedChart').getContext('2d');
    let problemsChart;

    // 3. Doughnut Chart - Learning Distribution (Now dynamically fetched)
    const ctxDist = document.getElementById('learningDistChart').getContext('2d');
    let distChart;
    
    // Fetch Chart Data
    const loadCharts = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        
        try {
            // Fetch Weekly Data
            const weeklyRes = await fetch('http://localhost:1111/api/v1/analytics/weekly', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const weeklyData = await weeklyRes.json();
            
            if (weeklyData.success) {
                problemsChart = new Chart(ctxProblems, {
                    type: 'bar',
                    data: {
                        labels: weeklyData.data.labels,
                        datasets: [{
                            label: 'Problems Solved',
                            data: weeklyData.data.datasets[0].data,
                            backgroundColor: '#10b981',
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }

            // Fetch Distribution
            const distRes = await fetch('http://localhost:1111/api/v1/analytics/distribution', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const distData = await distRes.json();
            
            if (distData.success) {
                distChart = new Chart(ctxDist, {
                    type: 'doughnut',
                    data: {
                        labels: distData.data.labels,
                        datasets: [{
                            data: distData.data.datasets[0].data,
                            backgroundColor: ['#2563EB', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444', '#14b8a6'],
                            borderWidth: 0,
                            cutout: '70%'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'right' }
                        }
                    }
                });
            }
            
        } catch(error) {
            console.error("Failed to load chart data:", error);
        }
    };
    
    loadCharts();

    // 4. Radar Chart - Skills Comparison
    const ctxSkills = document.getElementById('skillsRadarChart').getContext('2d');
    new Chart(ctxSkills, {
        type: 'radar',
        data: {
            labels: ['Problem Solving', 'System Design', 'Communication', 'Speed', 'Accuracy'],
            datasets: [{
                label: 'Your Skills',
                data: [85, 60, 75, 90, 80],
                backgroundColor: 'rgba(37,99,235,0.2)',
                borderColor: '#2563EB',
                pointBackgroundColor: '#2563EB',
                borderWidth: 2
            },
            {
                label: 'Target',
                data: [90, 80, 85, 85, 95],
                backgroundColor: 'rgba(16,185,129,0.1)',
                borderColor: '#10b981',
                borderDash: [5, 5],
                pointBackgroundColor: '#10b981',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { display: true },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });

    // 5. Area Chart - Monthly Performance
    const ctxMonthly = document.getElementById('monthlyPerfChart').getContext('2d');
    new Chart(ctxMonthly, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Overall Score',
                data: [40, 55, 50, 75, 82, 88],
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139,92,246,0.2)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#8b5cf6',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { borderDash: [5, 5] } },
                x: { grid: { display: false } }
            }
        }
    });

    // Export Reports Simulation
    const exportBtns = document.querySelectorAll('.export-action-btn');
    exportBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-check-lg"></i> Downloaded';
                setTimeout(() => this.innerHTML = originalText, 2000);
            }, 1500);
        });
    });

});
