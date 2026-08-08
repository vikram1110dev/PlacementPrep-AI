document.addEventListener("DOMContentLoaded", function () {
    const API_BASE = '/api/v1'; 
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('resumeFileInput');
    const btnBrowse = document.getElementById('btnBrowse');
    const uploadStatus = document.getElementById('uploadStatus');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const inpJobDescription = document.getElementById('inpJobDescription');
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultsDashboard = document.getElementById('resultsDashboard');
    const resumeList = document.getElementById('resumeList');
    const btnDeleteResume = document.getElementById('btnDeleteResume');
    const historyList = document.getElementById('historyList');

    let currentUploadedResumeId = null;

    // Load initial resumes
    async function loadResumes() {
        try {
            const res = await fetch(`${API_BASE}/resume`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success && data.data && data.data.length > 0) {
                renderResumeList(data.data);
            } else {
                resumeList.innerHTML = '<div class="text-muted small">No resumes found. Please upload one.</div>';
                btnDeleteResume.classList.add('d-none');
            }
        } catch (e) {
            resumeList.innerHTML = '<div class="text-danger small">Failed to load resumes.</div>';
        }
    }

    function renderResumeList(resumes) {
        resumeList.innerHTML = '';
        resumes.forEach(r => {
            const activeClass = r.id === currentUploadedResumeId ? 'active bg-light border-primary' : '';
            const html = `
                <a href="#" class="list-group-item list-group-item-action ${activeClass} resume-item" data-id="${r.id}">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1 text-truncate" style="max-width: 80%;">${r.title || 'Untitled Resume'}</h6>
                        <small class="text-muted">${r.is_uploaded ? '<i class="bi bi-cloud-arrow-up"></i>' : '<i class="bi bi-layout-text-sidebar"></i>'}</small>
                    </div>
                </a>
            `;
            resumeList.insertAdjacentHTML('beforeend', html);
        });

        if (currentUploadedResumeId) {
            btnDeleteResume.classList.remove('d-none');
        }

        document.querySelectorAll('.resume-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                const id = e.currentTarget.dataset.id;
                currentUploadedResumeId = id;
                renderResumeList(resumes);
                loadHistory(id);
                resultsDashboard.classList.add('d-none'); // Hide dashboard until analyzed
            });
        });
    }

    btnDeleteResume.addEventListener('click', async () => {
        if(!currentUploadedResumeId) return;
        if(!confirm('Are you sure you want to delete this resume?')) return;
        
        try {
            await fetch(`${API_BASE}/resume/${currentUploadedResumeId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            currentUploadedResumeId = null;
            resultsDashboard.classList.add('d-none');
            loadResumes();
        } catch (e) {
            alert('Failed to delete resume');
        }
    });

    async function loadHistory(id) {
        historyList.innerHTML = '<div class="text-muted small">Loading history...</div>';
        try {
            const res = await fetch(`${API_BASE}/resume/${id}/history`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success && data.data && data.data.length > 0) {
                historyList.innerHTML = '';
                data.data.forEach(h => {
                    const date = new Date(h.generated_at).toLocaleString();
                    const score = h.overall_score || h.match_percentage || 0;
                    const type = h.job_description ? 'Job Match' : 'General ATS';
                    const html = `
                        <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor:pointer;" onclick="renderDashboardFromHistory(this)" data-report='${JSON.stringify(h)}'>
                            <div>
                                <h6 class="mb-0 fw-bold">${type}</h6>
                                <small class="text-muted">${date}</small>
                            </div>
                            <span class="badge bg-primary rounded-pill">${score}%</span>
                        </div>
                    `;
                    historyList.insertAdjacentHTML('beforeend', html);
                });
            } else {
                historyList.innerHTML = '<div class="text-muted small">No history available for this resume.</div>';
            }
        } catch (e) {
            historyList.innerHTML = '<div class="text-danger small">Failed to load history.</div>';
        }
    }

    // Call loadResumes on startup
    loadResumes();

    // Drag and Drop Logic
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    btnBrowse.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            handleFileUpload(this.files[0]);
        }
    });

    async function handleFileUpload(file) {
        if(file.size > 5 * 1024 * 1024) {
            uploadStatus.innerHTML = '<span class="text-danger">File exceeds 5MB limit.</span>';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name);

        uploadStatus.innerHTML = '<span class="text-primary"><div class="spinner-border spinner-border-sm"></div> Uploading and parsing text...</span>';
        
        try {
            const res = await fetch(`${API_BASE}/resume/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            const data = await res.json();
            
            if(data.success) {
                currentUploadedResumeId = data.data.id;
                uploadStatus.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill"></i> Uploaded successfully! Ready for analysis.</span>';
                loadResumes();
            } else {
                uploadStatus.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle-fill"></i> ${data.detail || 'Upload failed'}</span>`;
            }
        } catch(e) {
            uploadStatus.innerHTML = '<span class="text-danger">Network error during upload.</span>';
        }
    }

    btnAnalyze.addEventListener('click', async () => {
        if(!currentUploadedResumeId) {
            alert('Please upload a resume first.');
            return;
        }

        const jdText = inpJobDescription.value.trim();
        
        resultsDashboard.classList.add('d-none');
        loadingOverlay.classList.remove('d-none');
        loadingOverlay.classList.add('d-flex');

        try {
            let endpoint = `${API_BASE}/resume/${currentUploadedResumeId}/analyze`;
            let options = {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            };

            if (jdText.length > 0) {
                if (jdText.length < 50) {
                    alert('Job description is too short. Please paste a proper JD or clear it to run a general analysis.');
                    loadingOverlay.classList.add('d-none');
                    loadingOverlay.classList.remove('d-flex');
                    return;
                }
                endpoint = `${API_BASE}/resume/${currentUploadedResumeId}/match-job`;
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify({ job_description: jdText });
            }

            const res = await fetch(endpoint, options);
            const data = await res.json();

            loadingOverlay.classList.add('d-none');
            loadingOverlay.classList.remove('d-flex');

            if (data.success) {
                renderDashboard(data.data, !!jdText);
                loadHistory(currentUploadedResumeId);
            } else {
                alert('Analysis failed: ' + (data.detail || 'Unknown error'));
            }
        } catch(e) {
            loadingOverlay.classList.add('d-none');
            loadingOverlay.classList.remove('d-flex');
            alert('Network error during analysis.');
        }
    });

    window.renderDashboardFromHistory = function(element) {
        const report = JSON.parse(element.dataset.report);
        renderDashboard(report, !!report.job_description);
    };

    function renderDashboard(report, isJobMatch) {
        resultsDashboard.classList.remove('d-none');

        const score = report.overall_score || 0;
        document.getElementById('overallScoreRing').style.setProperty('--score', `${score}%`);
        
        let colorClass = 'text-danger';
        if (score >= 70) colorClass = 'text-warning';
        if (score >= 85) colorClass = 'text-success';
        
        const scoreEl = document.getElementById('overallScoreText');
        scoreEl.innerText = score;
        scoreEl.className = `ats-ring-value ${colorClass}`;

        document.getElementById('matchTextIndicator').innerText = isJobMatch ? "JD Match Percentage" : "General ATS Score";

        document.getElementById('formattingScore').innerText = report.formatting_score ? `${report.formatting_score}%` : 'N/A';
        document.getElementById('completenessScore').innerText = report.section_completeness ? `${report.section_completeness}%` : 'N/A';

        // Keywords
        const matchedList = document.getElementById('matchedSkillsList');
        matchedList.innerHTML = '';
        (report.keyword_matches || []).forEach(kw => {
            matchedList.innerHTML += `<span class="badge bg-success bg-opacity-10 text-success border border-success">${kw}</span>`;
        });
        if(!report.keyword_matches || report.keyword_matches.length === 0) matchedList.innerHTML = '<span class="text-muted small">None found.</span>';

        const missingList = document.getElementById('missingSkillsList');
        missingList.innerHTML = '';
        (report.missing_skills || []).forEach(kw => {
            missingList.innerHTML += `<span class="badge bg-danger bg-opacity-10 text-danger border border-danger">${kw}</span>`;
        });
        if(!report.missing_skills || report.missing_skills.length === 0) missingList.innerHTML = '<span class="text-muted small">None found.</span>';

        // Bullets
        const bulletsAccordion = document.getElementById('bulletsAccordion');
        bulletsAccordion.innerHTML = '';
        const bullets = report.bullet_improvements || [];
        
        if (bullets.length === 0) {
            bulletsAccordion.innerHTML = '<div class="text-muted small">No bullet points needed improvements, or they could not be extracted!</div>';
        } else {
            bullets.forEach((b, idx) => {
                const accId = `bulletAcc${idx}`;
                const hHTML = `
                <div class="accordion-item mb-2 border rounded">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#${accId}">
                            <i class="bi bi-x-circle-fill text-danger me-2"></i> 
                            <span class="text-truncate" style="max-width: 80%; font-size: 0.85rem;">${b.original}</span>
                        </button>
                    </h2>
                    <div id="${accId}" class="accordion-collapse collapse" data-bs-parent="#bulletsAccordion">
                        <div class="accordion-body bg-light">
                            <p class="small text-muted mb-1 fw-bold">Original:</p>
                            <p class="small text-danger mb-3">${b.original}</p>
                            <p class="small text-muted mb-1 fw-bold">AI Suggestion (Action + Task + Result):</p>
                            <p class="small text-success mb-3 fw-medium">${b.suggested}</p>
                            <div class="badge bg-warning text-dark"><i class="bi bi-info-circle"></i> ${b.reason}</div>
                        </div>
                    </div>
                </div>`;
                bulletsAccordion.innerHTML += hHTML;
            });
        }
    }
});
