document.addEventListener("DOMContentLoaded", function () {
    // 1. Animate Circular Progress Bar
    const circularProgress = document.querySelector('.circular-progress');
    const progressValue = document.querySelector('.circular-progress-value');
    
    if (circularProgress && progressValue) {
        let progressStartValue = 0;
        let progressEndValue = 75; // Represents 75% accuracy
        let speed = 20;
        
        let progress = setInterval(() => {
            progressStartValue++;
            progressValue.textContent = `${progressStartValue}%`;
            circularProgress.style.background = `conic-gradient(#2563EB ${progressStartValue * 3.6}deg, #e5e7eb 0deg)`;
            
            if(progressStartValue === progressEndValue) {
                clearInterval(progress);
            }
        }, speed);
    }

    // 2. Mock Filter Functionality
    const filterBtn = document.getElementById('filterBtn');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            alert('Filter modal will open here to sort by difficulty, topic, or completion status.');
        });
    }

    // 3. Start Button interactions
    const startBtns = document.querySelectorAll('.btn-outline-primary, .btn-primary');
    startBtns.forEach(btn => {
        // Exclude sidebar and navbar buttons
        if(!btn.closest('.sidebar') && !btn.closest('.top-navbar')) {
            btn.addEventListener('click', function(e) {
                if(this.textContent.includes('Start') || this.textContent.includes('Continue')) {
                    e.preventDefault();
                    // Just a visual effect for demo
                    const originalText = this.innerHTML;
                    this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                    this.classList.add('disabled');
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.remove('disabled');
                        // In real app, redirect to test page
                    }, 1000);
                }
            });
        }
    });
});
