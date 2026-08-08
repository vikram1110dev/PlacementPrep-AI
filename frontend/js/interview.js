const API_BASE = 'http://localhost:1111/api/v1/interview';
const token = localStorage.getItem('token');

if (!token) {
    window.location.href = 'login.html';
}

const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
};

// --- Setup ---
async function startInterview(event) {
    event.preventDefault();
    const btn = document.getElementById('startBtn');
    btn.textContent = 'Preparing AI...';
    btn.disabled = true;

    const data = {
        interview_type: document.getElementById('type').value,
        role: document.getElementById('role').value,
        company: document.getElementById('company').value || null,
        difficulty: document.getElementById('difficulty').value,
        num_questions: parseInt(document.getElementById('questions').value)
    };

    try {
        const response = await fetch(`${API_BASE}/start`, {
            method: 'POST',
            headers,
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            sessionStorage.setItem('interview_session_id', result.data.session_id);
            window.location.href = 'interview-session.html';
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error(error);
        alert('Failed to start interview.');
    } finally {
        btn.textContent = 'Start Interview';
        btn.disabled = false;
    }
}

// --- Session ---
async function loadSession() {
    const sessionId = sessionStorage.getItem('interview_session_id');
    if (!sessionId) {
        window.location.href = 'interview-setup.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/${sessionId}`, { headers });
        const result = await response.json();
        if (result.success) {
            updateSessionUI(result.data);
        }
    } catch (error) {
        console.error(error);
    }
}

function updateSessionUI(state) {
    if (state.is_complete) {
        window.location.href = 'interview-report.html';
        return;
    }

    document.getElementById('progress-text').textContent = `Question ${state.questions_answered + 1} of ${state.total_questions}`;
    const progressPercent = (state.questions_answered / state.total_questions) * 100;
    document.getElementById('progress-bar-fill').style.width = `${progressPercent}%`;

    document.getElementById('question-text').textContent = state.current_question.question_text;
    document.getElementById('answer-input').value = '';
    document.getElementById('evaluation-box').style.display = 'none';
    
    document.getElementById('submitBtn').style.display = 'block';
    document.getElementById('nextBtn').style.display = 'none';
}

async function submitAnswer() {
    const sessionId = sessionStorage.getItem('interview_session_id');
    const answer = document.getElementById('answer-input').value.trim();
    if (!answer) return;

    const btn = document.getElementById('submitBtn');
    btn.textContent = 'Evaluating...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/${sessionId}/answer`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ answer_text: answer })
        });
        const result = await response.json();
        if (result.success) {
            showEvaluation(result.data.evaluation);
            document.getElementById('submitBtn').style.display = 'none';
            document.getElementById('nextBtn').style.display = 'block';
        }
    } catch (error) {
        console.error(error);
        alert('Evaluation failed');
    } finally {
        btn.textContent = 'Submit Answer';
        btn.disabled = false;
    }
}

function showEvaluation(eval) {
    const box = document.getElementById('evaluation-box');
    box.style.display = 'block';
    document.getElementById('eval-score').textContent = eval.score.toFixed(1);
    document.getElementById('eval-good').textContent = eval.feedback_good;
    document.getElementById('eval-improve').textContent = eval.feedback_improve;
}

async function loadNextQuestion() {
    loadSession(); // This will fetch the latest state and either show the next question or redirect to report
}

// --- Report ---
async function loadReport() {
    const sessionId = sessionStorage.getItem('interview_session_id');
    if (!sessionId) return;

    try {
        const response = await fetch(`${API_BASE}/${sessionId}/report`, { headers });
        const result = await response.json();
        if (result.success) {
            const r = result.data;
            document.getElementById('overall-score').textContent = `${(r.overall_score || 0).toFixed(1)} / 10`;
            document.getElementById('role-display').textContent = `${r.role} (${r.interview_type})`;
            document.getElementById('feedback-strengths').textContent = r.feedback_strengths || 'N/A';
            document.getElementById('feedback-weaknesses').textContent = r.feedback_weaknesses || 'N/A';
            document.getElementById('feedback-improvements').textContent = r.feedback_improvements || 'N/A';
        }
    } catch (error) {
        console.error(error);
    }
}

// --- History ---
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/user/history`, { headers });
        const result = await response.json();
        if (result.success) {
            const tbody = document.getElementById('history-tbody');
            tbody.innerHTML = '';
            result.data.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${new Date(s.start_time).toLocaleDateString()}</td>
                    <td>${s.role}</td>
                    <td>${s.interview_type}</td>
                    <td>${s.overall_score ? s.overall_score.toFixed(1) : '-'} / 10</td>
                    <td>${s.status}</td>
                    <td>
                        ${s.status === 'completed' ? `<a href="#" onclick="viewReport('${s.session_id}')" style="color: var(--primary-color);">View Report</a>` : ''}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error(error);
    }
}

function viewReport(sessionId) {
    sessionStorage.setItem('interview_session_id', sessionId);
    window.location.href = 'interview-report.html';
}
