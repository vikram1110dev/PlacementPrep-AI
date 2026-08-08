document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = '/api/v1'; 
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Generate GitHub Style Heatmap
    const heatmapGrid = document.getElementById('heatmapGrid');
    if (heatmapGrid) {
        const daysToGenerate = 364;
        for (let i = 0; i < daysToGenerate; i++) {
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            const rand = Math.random();
            if (rand > 0.95) cell.classList.add('level-4');
            else if (rand > 0.85) cell.classList.add('level-3');
            else if (rand > 0.70) cell.classList.add('level-2');
            else if (rand > 0.50) cell.classList.add('level-1');
            heatmapGrid.appendChild(cell);
        }
        const heatmapContainer = document.querySelector('.heatmap-container');
        if (heatmapContainer) {
            heatmapContainer.scrollLeft = heatmapContainer.scrollWidth;
        }
    }

    // Fetch and render problems
    async function loadProblems() {
        try {
            const res = await fetch(`${API_BASE}/dsa/problems`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                renderProblemTable(data.data);
            }
        } catch (e) {
            console.error(e);
        }
    }

    // Fetch progress
    async function loadProgress() {
        try {
            const res = await fetch(`${API_BASE}/dsa/progress`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                const p = data.data;
                const progressDiv = document.querySelector('.dash-card h3.text-primary');
                if(progressDiv) {
                    const stats = document.querySelectorAll('.progress-stat h3');
                    if (stats.length >= 4) {
                        stats[0].innerText = p.total_solved;
                        stats[1].innerText = p.easy_solved;
                        stats[2].innerText = p.medium_solved;
                        stats[3].innerText = p.hard_solved;
                    }
                }
            }
        } catch(e) {
            console.error(e);
        }
    }

    function renderProblemTable(problems) {
        const tbody = document.querySelector('.table tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        problems.forEach(p => {
            let statusIcon = '<i class="bi bi-circle text-muted"></i>';
            if (p.status === 'Solved') {
                statusIcon = '<i class="bi bi-check-circle-fill text-success"></i>';
            } else if (p.status === 'Attempted') {
                statusIcon = '<i class="bi bi-exclamation-circle text-warning"></i>';
            }
            
            let badgeClass = p.difficulty === 'easy' ? 'badge-easy' : (p.difficulty === 'medium' ? 'badge-medium' : 'badge-hard');
            
            tbody.innerHTML += `
                <tr>
                    <td>${statusIcon}</td>
                    <td>
                        <a href="coding.html?id=${p.id}" class="fw-bold text-dark text-decoration-none problem-link">${p.title}</a>
                    </td>
                    <td><span class="badge ${badgeClass}">${p.difficulty}</span></td>
                    <td><span class="text-muted small">${p.category}</span></td>
                    <td><button class="btn btn-sm btn-light border"><i class="bi bi-play-fill text-success"></i></button></td>
                </tr>
            `;
        });
    }

    async function loadRecommendations() {
        try {
            const res = await fetch(`${API_BASE}/dsa/recommendations`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                renderRecommendations(data.data);
            }
        } catch(e) {
            console.error(e);
        }
    }

    function renderRecommendations(recs) {
        const container = document.querySelector('.problem-list');
        if (!container) return;

        if (recs.length === 0) {
            container.innerHTML = '<div class="text-muted">No recommendations at this time. Keep solving!</div>';
            return;
        }

        container.innerHTML = recs.map(r => {
            let badgeClass = r.difficulty === 'easy' ? 'badge-easy' : (r.difficulty === 'medium' ? 'badge-medium' : 'badge-hard');
            return `
                <div class="problem-item p-3 d-flex justify-content-between align-items-center flex-wrap gap-3">
                    <div>
                        <h6 class="fw-bold mb-1">${r.title}</h6>
                        <div class="d-flex gap-3 text-muted small fw-medium">
                            <span class="badge ${badgeClass}">${r.difficulty}</span>
                            <span>${r.category}</span>
                            <span class="text-primary"><i class="bi bi-lightbulb-fill me-1"></i>${r.reason}</span>
                        </div>
                    </div>
                    <div class="d-flex align-items-center gap-3">
                        <button class="btn btn-outline-primary btn-sm px-4 rounded-pill" onclick="window.location.href='coding.html?id=${r.id}'">Solve</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    loadProgress();
    loadProblems();
    loadRecommendations();
});
