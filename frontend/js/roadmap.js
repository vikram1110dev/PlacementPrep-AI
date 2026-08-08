const API_BASE = 'http://localhost:1111/api/v1/roadmap';
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = 'login.html';
}

const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
};

let currentTask = null;

async function loadRoadmap() {
    try {
        document.getElementById('loading-state').classList.remove('hidden');
        document.getElementById('setup-view').classList.add('hidden');
        document.getElementById('roadmap-view').classList.add('hidden');

        const response = await fetch(`${API_BASE}/current`, { headers });
        const result = await response.json();

        document.getElementById('loading-state').classList.add('hidden');

        if (result.success && result.data) {
            renderRoadmap(result.data);
        } else {
            // Show setup
            document.getElementById('setup-view').classList.remove('hidden');
        }
    } catch (error) {
        console.error(error);
        alert('Failed to load roadmap.');
    }
}

async function generateRoadmap(event) {
    event.preventDefault();
    const btn = document.getElementById('genBtn');
    btn.textContent = 'Analyzing Profile...';
    btn.disabled = true;

    const data = {
        target_role: document.getElementById('role').value,
        target_company: document.getElementById('company').value || null,
        duration_weeks: parseInt(document.getElementById('duration').value),
        daily_time_minutes: parseInt(document.getElementById('time').value)
    };

    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers,
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            renderRoadmap(result.data);
        }
    } catch (error) {
        console.error(error);
        alert('Failed to generate roadmap.');
    } finally {
        btn.textContent = 'Generate My Roadmap';
        btn.disabled = false;
    }
}

function renderRoadmap(data) {
    document.getElementById('setup-view').classList.add('hidden');
    document.getElementById('roadmap-view').classList.remove('hidden');

    document.getElementById('role-display').textContent = data.target_role + (data.target_company ? ` at ${data.target_company}` : '');
    document.getElementById('ai-summary').textContent = data.ai_recommendation_summary || '';
    
    document.getElementById('progress-text').textContent = `${data.completion_percentage.toFixed(0)}% Completed`;
    document.getElementById('progress-bar-fill').style.width = `${data.completion_percentage}%`;

    const container = document.getElementById('weeks-container');
    container.innerHTML = '';

    data.weeks.forEach(week => {
        const section = document.createElement('div');
        section.className = 'week-section';
        
        section.innerHTML = `
            <div class="week-title">Week ${week.week_number}: ${week.focus_area || 'Practice'}</div>
            <div class="task-grid" id="week-${week.id}"></div>
        `;
        container.appendChild(section);

        const grid = document.getElementById(`week-${week.id}`);
        week.tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = `task-card task-status-${task.status}`;
            card.innerHTML = `
                <div class="task-topic">Day ${task.day_number}: ${task.topic}</div>
                <div class="task-meta">${task.estimated_time} mins | ${task.difficulty || 'Medium'}</div>
                <div class="task-meta" style="margin-top: 0.5rem; font-style: italic;">Status: ${task.status.replace('_', ' ')}</div>
            `;
            // Store task data directly on the element for the click handler
            card.onclick = () => openTaskModal(task);
            grid.appendChild(card);
        });
    });
}

function openTaskModal(task) {
    currentTask = task;
    document.getElementById('modal-topic').textContent = `Day ${task.day_number}: ${task.topic}`;
    document.getElementById('modal-activity').textContent = task.activity;
    document.getElementById('modal-outcome').textContent = task.expected_outcome || 'N/A';
    
    document.getElementById('task-modal').classList.remove('hidden');
}

function closeTaskModal() {
    document.getElementById('task-modal').classList.add('hidden');
    currentTask = null;
}

async function updateTaskStatus(status) {
    if (!currentTask) return;
    
    try {
        const response = await fetch(`${API_BASE}/task/${currentTask.id}/status`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ status })
        });
        const result = await response.json();
        if (result.success) {
            closeTaskModal();
            loadRoadmap(); // Reload to update UI and progress
        }
    } catch (error) {
        console.error(error);
        alert('Failed to update task status.');
    }
}
