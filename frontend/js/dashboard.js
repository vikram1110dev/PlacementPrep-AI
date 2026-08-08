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

    // Fetch Analytics Data
    const fetchDashboardData = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            // Fetch Overview
            const overviewRes = await fetch('http://localhost:1111/api/v1/analytics/dashboard', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const overviewData = await overviewRes.json();
            
            if (overviewData.success) {
                const data = overviewData.data;
                document.getElementById('dashStudyTime').innerText = data.total_study_time_minutes;
                document.getElementById('dashStreak').innerText = data.current_streak;
                document.getElementById('dashSolved').innerText = data.questions_solved;
                document.getElementById('dashScore').innerText = data.average_score.toFixed(1);
            }

            // Fetch Leaderboard
            const lbRes = await fetch('http://localhost:1111/api/v1/analytics/leaderboard', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const lbData = await lbRes.json();
            
            if (lbData.success) {
                const lbContainer = document.getElementById('dashLeaderboard');
                lbContainer.innerHTML = '';
                lbData.data.forEach((user, index) => {
                    let rankClass = index === 0 ? 'rank-1' : (index === 1 ? 'rank-2' : (index === 2 ? 'rank-3' : 'bg-light text-muted'));
                    lbContainer.innerHTML += `
                        <div class="leaderboard-item">
                            <div class="rank-badge ${rankClass} me-3 shadow-sm">${user.rank}</div>
                            <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random" class="rounded-circle me-3" width="40" height="40">
                            <div class="flex-grow-1">
                                <h6 class="mb-0 fw-bold fs-6">${user.name}</h6>
                                <small class="text-muted fw-medium">Level ${user.level}</small>
                            </div>
                            <div class="fw-bold text-primary">${user.xp} XP</div>
                        </div>
                    `;
                });
            }

            // Fetch Recent Activity
            const recentRes = await fetch('http://localhost:1111/api/v1/analytics/recent', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const recentData = await recentRes.json();
            
            if (recentData.success) {
                const recentContainer = document.getElementById('dashRecentActivity');
                recentContainer.innerHTML = '';
                
                if (recentData.data.length === 0) {
                    recentContainer.innerHTML = '<li class="timeline-item"><p class="text-muted small mb-0">No recent activity.</p></li>';
                }
                
                recentData.data.forEach((item, index) => {
                    const dateStr = new Date(item.completed_time).toLocaleString();
                    const markerColor = index % 2 === 0 ? 'bg-success border-success' : 'bg-primary border-primary';
                    recentContainer.innerHTML += `
                        <li class="timeline-item">
                            <div class="timeline-marker ${markerColor}"></div>
                            <h6 class="fw-semibold mb-1">Aptitude Test Completed</h6>
                            <p class="text-muted small mb-0">Score: ${item.score} • ${dateStr}</p>
                        </li>
                    `;
                });
            }
            
            // Fetch Current Roadmap Tasks
            const roadmapRes = await fetch('http://localhost:1111/api/v1/roadmap/current', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const roadmapData = await roadmapRes.json();
            
            const tasksContainer = document.getElementById('dashTodayTasks');
            if (roadmapData.success && roadmapData.data) {
                const activeWeek = roadmapData.data.weeks[0]; // simplistic assumption: show week 1 tasks
                if (activeWeek && activeWeek.tasks.length > 0) {
                    tasksContainer.innerHTML = '';
                    activeWeek.tasks.slice(0, 4).forEach(task => { // show up to 4 tasks
                        const isChecked = task.status === 'completed' ? 'checked' : '';
                        const titleClass = task.status === 'completed' ? 'text-decoration-line-through text-muted' : '';
                        
                        tasksContainer.innerHTML += `
                            <div class="task-item" style="padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color); display: flex; align-items: flex-start;">
                                <input type="checkbox" class="form-check-input me-3 mt-1" ${isChecked} disabled>
                                <div>
                                    <h6 class="mb-1 fw-medium ${titleClass}">${task.topic}</h6>
                                    <small class="text-muted fw-medium">${task.estimated_time} mins | ${task.difficulty || 'Medium'}</small>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    tasksContainer.innerHTML = '<div class="p-4 text-muted small">No tasks available for today.</div>';
                }
            } else {
                tasksContainer.innerHTML = '<div class="p-4 text-muted small">No active roadmap. <a href="roadmap.html">Create one</a></div>';
            }

        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    };

    fetchDashboardData();
});
