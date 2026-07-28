document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Generate GitHub Style Heatmap
    const heatmapGrid = document.getElementById('heatmapGrid');
    if (heatmapGrid) {
        // Generate roughly 52 weeks * 7 days = 364 squares
        const daysToGenerate = 364;
        
        for (let i = 0; i < daysToGenerate; i++) {
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            
            // Randomly assign activity levels for demo purposes
            // Heavy bias towards 0 (no activity)
            const rand = Math.random();
            if (rand > 0.95) {
                cell.classList.add('level-4');
            } else if (rand > 0.85) {
                cell.classList.add('level-3');
            } else if (rand > 0.70) {
                cell.classList.add('level-2');
            } else if (rand > 0.50) {
                cell.classList.add('level-1');
            }
            // else remains level-0 (default gray)
            
            heatmapGrid.appendChild(cell);
        }
        
        // Scroll heatmap to the end (most recent)
        const heatmapContainer = document.querySelector('.heatmap-container');
        if (heatmapContainer) {
            heatmapContainer.scrollLeft = heatmapContainer.scrollWidth;
        }
    }
    
    // 2. Company Pills Active Toggle
    const companyPills = document.querySelectorAll('.company-pill');
    companyPills.forEach(pill => {
        pill.addEventListener('click', function() {
            companyPills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // 3. Mock Code Editor Run Action
    const runBtn = document.getElementById('runCodeBtn');
    const submitBtn = document.getElementById('submitCodeBtn');
    const consoleOutput = document.getElementById('consoleOutput');
    
    if (runBtn && consoleOutput) {
        runBtn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...';
            this.disabled = true;
            consoleOutput.innerHTML = '<span class="text-white-50">Compiling and executing...</span>';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                consoleOutput.innerHTML = '<span class="text-success">Success! All test cases passed.</span><br><span class="text-white-50">Runtime: 12 ms<br>Memory: 41.2 MB</span>';
            }, 1500);
        });
    }
    
    if (submitBtn && consoleOutput) {
        submitBtn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            this.disabled = true;
            consoleOutput.innerHTML = '<span class="text-white-50">Running against hidden test cases...</span>';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                consoleOutput.innerHTML = '<span class="text-success fw-bold">Accepted! +150 XP</span><br><span class="text-white-50">Your solution beats 95% of users.</span>';
                
                // Trigger confetti or similar animation here in a real app
            }, 2000);
        });
    }
    
    // 4. Progress Rings Animation
    const rings = document.querySelectorAll('.progress-ring');
    rings.forEach(ring => {
        const value = parseInt(ring.getAttribute('data-percent') || '0');
        const color = ring.getAttribute('data-color') || '#2563eb';
        ring.style.background = `conic-gradient(${color} ${value * 3.6}deg, #e5e7eb 0deg)`;
    });
});
