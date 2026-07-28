document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Filter Pills Toggle
    const filterPills = document.querySelectorAll('.filter-pill');
    filterPills.forEach(pill => {
        pill.addEventListener('click', function() {
            // Find siblings in the same wrapper
            const wrapper = this.closest('.filter-wrapper');
            wrapper.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // 2. Project Card Selection
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Prevent if clicked on a button inside the card
            if (e.target.tagName.toLowerCase() === 'button' || e.target.closest('button')) {
                return;
            }
            
            const title = this.querySelector('h5').textContent;
            document.getElementById('activeProjectTitle').textContent = title;
            
            // Smooth scroll to workspace
            document.getElementById('projectWorkspace').scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // 3. Save Button Toggle
    const saveBtns = document.querySelectorAll('.btn-save-project');
    saveBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-bookmark')) {
                icon.classList.remove('bi-bookmark');
                icon.classList.add('bi-bookmark-fill');
                this.classList.add('text-primary');
            } else {
                icon.classList.remove('bi-bookmark-fill');
                icon.classList.add('bi-bookmark');
                this.classList.remove('text-primary');
            }
        });
    });

    // 4. Project Submission Logic
    const submitBtn = document.getElementById('submitProjectBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            const githubUrl = document.getElementById('githubUrl').value;
            if (!githubUrl) {
                alert('Please provide at least a GitHub Repository URL.');
                return;
            }
            
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-check-circle-fill"></i> Submitted Successfully';
                this.classList.remove('btn-primary');
                this.classList.add('btn-success');
                
                // Show review section mock
                const reviewSection = document.getElementById('projectReviewSection');
                if(reviewSection) reviewSection.classList.remove('d-none');
                
            }, 1500);
        });
    }

    // 5. Update Progress Bar Demo
    setTimeout(() => {
        const progressBar = document.getElementById('projectProgressBar');
        if(progressBar) {
            progressBar.style.width = '65%';
        }
    }, 500);
});
