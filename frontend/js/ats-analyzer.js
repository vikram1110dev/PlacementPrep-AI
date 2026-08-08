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

    let currentUploadedResumeId = null;

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
            } else {
                alert('Analysis failed: ' + (data.detail || 'Unknown error'));
            }
        } catch(e) {
            loadingOverlay.classList.add('d-none');
            loadingOverlay.classList.remove('d-flex');
            alert('Network error during analysis.');
        }
    });

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
