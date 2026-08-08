document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = '/api/v1'; 
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const problemId = urlParams.get('id');

    if (!problemId) {
        // If no ID is passed, just fetch the first problem and load it
        try {
            const res = await fetch(`${API_BASE}/dsa/problems`, { headers: { 'Authorization': `Bearer ${token}` } });
            const data = await res.json();
            if (data.success && data.data.length > 0) {
                window.location.href = `coding.html?id=${data.data[0].id}`;
            }
        } catch (e) {
            console.error(e);
        }
        return;
    }

    // 0. Fetch all problems for the sidebar
    async function loadProblemList() {
        try {
            const res = await fetch(`${API_BASE}/dsa/problems`, { headers: { 'Authorization': `Bearer ${token}` } });
            const data = await res.json();
            if (data.success) {
                renderProblemList(data.data);
            }
        } catch (e) {
            console.error(e);
        }
    }

    function renderProblemList(problems) {
        const container = document.querySelector('.problem-list-container');
        if (!container) return;
        
        container.innerHTML = '';
        problems.forEach(p => {
            const isActive = p.id === problemId ? 'active' : '';
            let statusIcon = '<i class="bi bi-dash-circle text-muted"></i>';
            if (p.status === 'Solved') {
                statusIcon = '<i class="bi bi-check-circle-fill text-success"></i>';
            } else if (p.status === 'Attempted') {
                statusIcon = '<i class="bi bi-exclamation-circle text-warning"></i>';
            }
            
            let badgeClass = p.difficulty === 'easy' ? 'badge-easy' : (p.difficulty === 'medium' ? 'badge-medium' : 'badge-hard');
            
            container.innerHTML += `
                <div class="problem-card p-3 ${isActive}" style="cursor: pointer;" onclick="window.location.href='coding.html?id=${p.id}'">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="fw-bold mb-0">${p.title}</h6>
                        ${statusIcon}
                    </div>
                    <div class="d-flex gap-2 text-muted small fw-medium mb-3">
                        <span class="badge ${badgeClass}">${p.difficulty}</span>
                        <span class="text-warning"><i class="bi bi-award"></i> XP</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex gap-1 text-muted small">
                            <span class="badge bg-light text-dark border">${p.category}</span>
                        </div>
                        <i class="bi bi-bookmark text-muted"></i>
                    </div>
                </div>
            `;
        });
    }

    loadProblemList();

    // 1. Fetch Problem Details
    async function loadProblem() {
        try {
            const res = await fetch(`${API_BASE}/dsa/problems/${problemId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                renderProblem(data.data);
            }
        } catch(e) {
            console.error(e);
        }
    }

    function renderProblem(problem) {
        document.getElementById('desc-tab').innerText = `Description: ${problem.title}`;
        document.querySelector('#description').innerHTML = `
            <div class="d-flex gap-2 align-items-center mb-3">
                <h4 class="fw-bold mb-0">${problem.title}</h4>
            </div>
            <div class="d-flex gap-3 text-muted small fw-medium mb-4">
                <span class="badge ${problem.difficulty === 'easy' ? 'badge-easy' : problem.difficulty === 'medium' ? 'badge-medium' : 'badge-hard'}">${problem.difficulty}</span>
                <span class="badge bg-light text-dark border">${problem.category}</span>
            </div>
            ${problem.description}
            
            <h6 class="fw-bold mt-4">Execution Specs:</h6>
            <ul class="small text-muted">
                <li>Time Limit: ${problem.time_limit}s</li>
                <li>Memory Limit: ${problem.memory_limit} MB</li>
            </ul>
        `;

        if (problem.starter_code) {
            document.getElementById('codeEditor').value = problem.starter_code;
        }

        const tcPanel = document.getElementById('consoleOutput');
        tcPanel.innerHTML = '';
        if (problem.test_cases && problem.test_cases.length > 0) {
            problem.test_cases.forEach((tc, idx) => {
                tcPanel.innerHTML += `
                    <div class="mb-3">
                        <small class="text-white-50 d-block mb-1">Sample Case ${idx+1} Input:</small>
                        <div class="bg-dark p-2 rounded text-light font-monospace small">${tc.input_data.replace(/\n/g, '<br>')}</div>
                    </div>
                    <div class="mb-4">
                        <small class="text-white-50 d-block mb-1">Expected Output:</small>
                        <div class="bg-dark p-2 rounded text-light font-monospace small">${tc.expected_output.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            });
        }
    }

    loadProblem();

    // 1.5 Fetch Submission History
    async function loadSubmissionHistory() {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        
        try {
            const res = await fetch(`${API_BASE}/dsa/submissions`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                const submissions = data.data.filter(s => s.problem_id === problemId);
                if (submissions.length === 0) {
                    historyList.innerHTML = '<div class="text-center text-muted py-4">No past submissions for this problem.</div>';
                    return;
                }
                
                historyList.innerHTML = submissions.map(s => {
                    const isAccepted = s.status === 'Accepted';
                    const color = isAccepted ? 'text-success' : 'text-danger';
                    const icon = isAccepted ? 'bi-check-circle-fill' : 'bi-x-circle-fill';
                    const date = new Date(s.submitted_at).toLocaleString();
                    
                    return `
                        <div class="border-bottom p-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="fw-bold mb-0 ${color}"><i class="bi ${icon} me-1"></i> ${s.status}</h6>
                                <span class="small text-muted">${date}</span>
                            </div>
                            <div class="d-flex gap-3 small fw-medium">
                                <span class="badge bg-light text-dark border">${s.language}</span>
                                <span>Passed: ${s.passed_tests}/${s.total_tests}</span>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        } catch(e) {
            console.error(e);
            historyList.innerHTML = '<div class="text-center text-danger py-4">Failed to load history.</div>';
        }
    }

    // Load history when tab is clicked for the first time or immediately
    const historyTab = document.getElementById('history-tab');
    if (historyTab) {
        historyTab.addEventListener('shown.bs.tab', () => {
            loadSubmissionHistory();
        });
    }

    // 2. Editor Toolbar Actions
    const copyBtn = document.getElementById('copyCodeBtn');
    const codeEditor = document.getElementById('codeEditor');
    
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            codeEditor.select();
            document.execCommand('copy');
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
            }, 2000);
        });
    }

    // 3. Run and Submit Logic
    const runBtn = document.getElementById('runCodeBtn');
    const submitBtn = document.getElementById('submitCodeBtn');
    const resultTabTrigger = document.querySelector('[data-bs-target="#submission"]');
    const testCasesTabTrigger = document.querySelector('[data-bs-target="#testcases"]');
    const langSelect = document.querySelector('.editor-toolbar select');

    if (runBtn) {
        runBtn.addEventListener('click', async function() {
            new bootstrap.Tab(testCasesTabTrigger).show();
            
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Running...';
            this.disabled = true;
            
            const consolePanel = document.getElementById('consoleOutput');
            consolePanel.innerHTML = '<span class="text-white-50">Executing in Judge0...</span>';
            
            try {
                const res = await fetch(`${API_BASE}/dsa/problems/${problemId}/run`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        language: langSelect.value,
                        code: codeEditor.value
                    })
                });
                
                const data = await res.json();
                this.innerHTML = originalText;
                this.disabled = false;
                
                if (data.success) {
                    const r = data.data;
                    let color = r.passed ? 'text-success' : 'text-danger';
                    consolePanel.innerHTML = `
                        <h6 class="${color} fw-bold">${r.status}</h6>
                        <hr class="border-secondary">
                        <small class="text-white-50 d-block mb-1">Your Output:</small>
                        <div class="bg-dark p-2 rounded text-light font-monospace small mb-3">${r.output || ''}</div>
                        <small class="text-white-50 d-block mb-1">Expected Output:</small>
                        <div class="bg-dark p-2 rounded text-light font-monospace small mb-3">${r.expected_output || ''}</div>
                        ${r.error_message ? `<small class="text-danger d-block mb-1">Error:</small><div class="bg-dark p-2 rounded text-danger font-monospace small mb-3">${r.error_message}</div>` : ''}
                        <small class="text-white-50">Time: ${r.execution_time}s | Memory: ${r.memory_usage}KB</small>
                    `;
                } else {
                    consolePanel.innerHTML = `<span class="text-danger">Error: ${data.detail}</span>`;
                }
            } catch(e) {
                this.innerHTML = originalText;
                this.disabled = false;
                consolePanel.innerHTML = '<span class="text-danger">Network Error</span>';
            }
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', async function() {
            new bootstrap.Tab(resultTabTrigger).show();
            
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Submitting...';
            this.disabled = true;
            
            document.getElementById('submissionPlaceholder').innerHTML = '<div class="spinner-border text-primary"></div><br>Evaluating all hidden test cases...';
            document.querySelector('.result-success').style.display = 'none';
            
            try {
                const res = await fetch(`${API_BASE}/dsa/problems/${problemId}/submit`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        language: langSelect.value,
                        code: codeEditor.value
                    })
                });
                
                const data = await res.json();
                this.innerHTML = originalText;
                this.disabled = false;
                
                document.getElementById('submissionPlaceholder').innerHTML = '';
                const resultDiv = document.querySelector('.result-success');
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    const r = data.data;
                    let isAccepted = r.status === 'Accepted';
                    let icon = isAccepted ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger';
                    let color = isAccepted ? 'text-success' : 'text-danger';
                    
                    resultDiv.innerHTML = `
                        <h4 class="fw-bold mb-3 ${color}"><i class="bi ${icon} me-2"></i>${r.status}</h4>
                        <div class="row g-3">
                            <div class="col-md-3">
                                <small class="d-block text-muted fw-semibold">Tests Passed</small>
                                <div class="fs-5 fw-bold">${r.passed_tests} / ${r.total_tests}</div>
                            </div>
                            <div class="col-md-3">
                                <small class="d-block text-muted fw-semibold">Total Runtime</small>
                                <div class="fs-5 fw-bold">${(r.execution_time * 1000).toFixed(0)} ms</div>
                            </div>
                            <div class="col-md-3">
                                <small class="d-block text-muted fw-semibold">Max Memory</small>
                                <div class="fs-5 fw-bold">${(r.memory_usage / 1024).toFixed(1)} MB</div>
                            </div>
                            <div class="col-md-3">
                                <small class="d-block text-muted fw-semibold">Reward</small>
                                <div class="fs-5 fw-bold text-warning">${isAccepted ? '+50 XP' : '+0 XP'}</div>
                            </div>
                        </div>
                        ${r.error_message ? `<hr><small class="text-danger d-block mb-1">Error Trace:</small><div class="bg-light p-3 rounded text-danger font-monospace small">${r.error_message}</div>` : ''}
                    `;
                } else {
                    resultDiv.innerHTML = `<h5 class="text-danger">Error: ${data.detail}</h5>`;
                }
            } catch(e) {
                this.innerHTML = originalText;
                this.disabled = false;
                document.getElementById('submissionPlaceholder').innerHTML = '<h5 class="text-danger">Network Error</h5>';
            }
        });
    }
});
