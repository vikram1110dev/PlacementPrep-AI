document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem('token');
    
    // Check if token exists
    if (!token) {
        // Optional: Redirect to login or just show placeholder data
        console.warn("No token found. Showing placeholder data.");
        return;
    }

    try {
        // 1. Fetch Progress Analytics
        const progressRes = await fetch('http://localhost:1111/api/v1/aptitude/progress', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const progressData = await progressRes.json();
        
        if (progressData.success && progressData.data) {
            const data = progressData.data;
            
            // Animate Circular Progress Bar
            const circularProgress = document.querySelector('.circular-progress');
            const progressValue = document.querySelector('.circular-progress-value');
            
            if (circularProgress && progressValue) {
                let progressStartValue = 0;
                let progressEndValue = Math.round(data.overall_accuracy);
                if (progressEndValue === 0) progressValue.textContent = '0%';
                
                let speed = 20;
                if(progressEndValue > 0) {
                    let progressInterval = setInterval(() => {
                        progressStartValue++;
                        progressValue.textContent = `${progressStartValue}%`;
                        circularProgress.style.background = `conic-gradient(#2563EB ${progressStartValue * 3.6}deg, #e5e7eb 0deg)`;
                        
                        if(progressStartValue === progressEndValue) {
                            clearInterval(progressInterval);
                        }
                    }, speed);
                }
            }

            // Update stats
            const solvedEl = document.querySelector('.dash-card h4.text-primary');
            if (solvedEl) solvedEl.textContent = data.total_tests_taken * 10; // Approx logic or use correct field
            
            const timeEl = document.querySelector('.dash-card h4.text-dark');
            if (timeEl) timeEl.textContent = `${data.time_spent_minutes}m`;
        }

        // 2. Fetch Topics (Demo for Quantitative Aptitude, assumes category_id 1)
        const topicsRes = await fetch('http://localhost:1111/api/v1/aptitude/topics', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const topicsData = await topicsRes.json();
        
        if (topicsData.success && topicsData.data) {
            window.availableTopics = topicsData.data;
            const select = document.getElementById('setupTopic');
            if (select) {
                topicsData.data.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.id;
                    opt.textContent = t.name;
                    select.appendChild(opt);
                });
            }
        }

    } catch (err) {
        console.error("Error fetching aptitude data", err);
    }

    let testModalInstance = null;
    if(document.getElementById('testSetupModal')) {
        testModalInstance = new bootstrap.Modal(document.getElementById('testSetupModal'));
    }

    const startBtns = document.querySelectorAll('.btn-outline-primary, .btn-primary');
    startBtns.forEach((btn, index) => {
        if(!btn.closest('.sidebar') && !btn.closest('.top-navbar') && btn.id !== 'startTestSubmitBtn') {
            btn.addEventListener('click', function(e) {
                if(this.textContent.includes('Start') || this.textContent.includes('Continue')) {
                    e.preventDefault();
                    if(testModalInstance) {
                        testModalInstance.show();
                    }
                }
            });
        }
    });

    const setupForm = document.getElementById('testSetupForm');
    if (setupForm) {
        setupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('startTestSubmitBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...';
            btn.disabled = true;

            const payload = {
                topic_id: document.getElementById('setupTopic').value ? parseInt(document.getElementById('setupTopic').value) : null,
                difficulty: document.getElementById('setupDifficulty').value || null,
                question_count: parseInt(document.getElementById('setupCount').value) || 10
            };

            try {
                const res = await fetch('http://localhost:1111/api/v1/aptitude/test/start', {
                    method: 'POST',
                    headers: { 
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                if (data.success) {
                    window.location.href = `aptitude-test.html?session=${data.data.session_id}`;
                } else {
                    alert("Error: " + (data.detail || data.message));
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }
            } catch(e) {
                console.error(e);
                alert("Failed to start test");
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }
});
