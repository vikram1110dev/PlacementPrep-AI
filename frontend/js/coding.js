document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Problem List Active State
    const problemCards = document.querySelectorAll('.problem-card');
    problemCards.forEach(card => {
        card.addEventListener('click', function() {
            problemCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // 2. Editor Toolbar Actions
    const formatBtn = document.getElementById('formatCodeBtn');
    const resetBtn = document.getElementById('resetCodeBtn');
    const copyBtn = document.getElementById('copyCodeBtn');
    const codeEditor = document.getElementById('codeEditor');
    
    if (formatBtn) {
        formatBtn.addEventListener('click', () => {
            alert('Code formatted successfully (Simulated)');
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if(confirm('Are you sure you want to reset your code to the default template?')) {
                alert('Code reset to default template.');
            }
        });
    }
    
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
    const consoleOutput = document.getElementById('consoleOutput');
    const resultTabTrigger = document.querySelector('[data-bs-target="#submission"]');
    const testCasesTabTrigger = document.querySelector('[data-bs-target="#testcases"]');
    
    if (runBtn && consoleOutput) {
        runBtn.addEventListener('click', function() {
            // Switch to Test Cases / Console tab
            const tab = new bootstrap.Tab(testCasesTabTrigger);
            tab.show();
            
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...';
            this.disabled = true;
            consoleOutput.innerHTML = '<span class="text-white-50">Compiling and running against public test cases...</span>';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                consoleOutput.innerHTML = '<span class="text-success">Success!</span><br><br>Test Case 1: Passed<br>Test Case 2: Passed<br>Test Case 3: Passed<br><br><span class="text-white-50">Runtime: 45 ms<br>Memory: 16.4 MB</span>';
            }, 1500);
        });
    }
    
    if (submitBtn && consoleOutput) {
        submitBtn.addEventListener('click', function() {
            // Switch to Submission tab
            const tab = new bootstrap.Tab(resultTabTrigger);
            tab.show();
            
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            this.disabled = true;
            consoleOutput.innerHTML = '<span class="text-white-50">Evaluating hidden test cases...</span>';
            
            // Hide previous results
            const resultSuccess = document.querySelector('.result-success');
            resultSuccess.style.display = 'none';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                consoleOutput.innerHTML = '<span class="text-success fw-bold">Accepted</span><br><span class="text-white-50">Output generated successfully. Check submission tab for details.</span>';
                
                // Show success card in submission tab
                resultSuccess.style.display = 'block';
                
            }, 2000);
        });
    }
    
    // 4. Hint Reveal Logic
    const hintBtns = document.querySelectorAll('.btn-reveal-hint');
    hintBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const hintText = this.nextElementSibling;
            hintText.classList.remove('d-none');
            this.classList.add('d-none');
        });
    });
});
