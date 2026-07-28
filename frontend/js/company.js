document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Filter Pills Toggle
    const filterPills = document.querySelectorAll('.filter-pill');
    filterPills.forEach(pill => {
        pill.addEventListener('click', function() {
            filterPills.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            
            // In a real app, this would filter the company cards
            // Here we just simulate a UI change
            console.log("Filtering by: " + this.textContent);
        });
    });

    // 2. Company Cards Selection Logic
    const companyCards = document.querySelectorAll('.company-card');
    companyCards.forEach(card => {
        card.addEventListener('click', function() {
            companyCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            const companyName = this.querySelector('h5').textContent;
            
            // Update the company details header dynamically (Simulated)
            document.getElementById('detailsCompanyName').textContent = companyName;
            document.getElementById('detailsCompanyTitle').textContent = companyName + " Preparation Hub";
            
            // Smooth scroll to details section
            document.querySelector('.company-details-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // 3. Eligibility Checker Logic
    const checkEligibilityBtn = document.getElementById('checkEligibilityBtn');
    if (checkEligibilityBtn) {
        checkEligibilityBtn.addEventListener('click', function() {
            const cgpa = document.getElementById('cgpaInput').value;
            const backlogs = document.getElementById('backlogsInput').value;
            const resultBox = document.getElementById('eligibilityResult');
            const resultContent = document.getElementById('eligibilityContent');
            
            if (!cgpa || !backlogs) {
                alert("Please fill all fields to check eligibility.");
                return;
            }

            // Simple mock logic for eligibility (e.g. Google requires > 7.0 CGPA and 0 backlogs)
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Checking...';
            this.disabled = true;

            setTimeout(() => {
                this.innerHTML = 'Check Eligibility';
                this.disabled = false;
                resultBox.style.display = 'block';
                
                if (parseFloat(cgpa) >= 7.0 && parseInt(backlogs) === 0) {
                    resultBox.className = 'eligibility-result bg-success bg-opacity-10 border border-success';
                    resultContent.innerHTML = `
                        <div class="d-flex align-items-center gap-3">
                            <i class="bi bi-check-circle-fill text-success fs-3"></i>
                            <div>
                                <h6 class="fw-bold text-success mb-1">You are Eligible!</h6>
                                <small class="text-dark">You meet the basic criteria for this company. Focus on your DSA and Core subjects.</small>
                            </div>
                        </div>`;
                } else {
                    resultBox.className = 'eligibility-result bg-danger bg-opacity-10 border border-danger';
                    resultContent.innerHTML = `
                        <div class="d-flex align-items-center gap-3">
                            <i class="bi bi-x-circle-fill text-danger fs-3"></i>
                            <div>
                                <h6 class="fw-bold text-danger mb-1">Not Eligible Currently</h6>
                                <small class="text-dark">Most product companies require at least 7.0 CGPA and 0 active backlogs. Clear your backlogs first.</small>
                            </div>
                        </div>`;
                }
            }, 1000);
        });
    }

    // 4. Mock Apply Buttons
    const applyBtns = document.querySelectorAll('.btn-apply-mock');
    applyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            alert('Redirecting to the company career portal...');
        });
    });
});
