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
            // Usually we would dynamically render topics here.
            // For MVP, if topics exist, we attach the redirect logic to Start buttons.
            window.availableTopics = topicsData.data;
        }

    } catch (err) {
        console.error("Error fetching aptitude data", err);
    }

    // 3. Start Button interactions (Redirect to test page)
    const startBtns = document.querySelectorAll('.btn-outline-primary, .btn-primary');
    startBtns.forEach((btn, index) => {
        if(!btn.closest('.sidebar') && !btn.closest('.top-navbar')) {
            btn.addEventListener('click', function(e) {
                if(this.textContent.includes('Start') || this.textContent.includes('Continue')) {
                    e.preventDefault();
                    
                    const originalText = this.innerHTML;
                    this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                    this.classList.add('disabled');
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.remove('disabled');
                        // In real app, topic ID should be derived from the card.
                        // For MVP, redirect to test page with dummy topic=1, difficulty=EASY
                        window.location.href = 'aptitude-test.html?topic=1&difficulty=EASY';
                    }, 500);
                }
            });
        }
    });
});
