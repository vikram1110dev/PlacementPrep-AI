document.addEventListener("DOMContentLoaded", function () {
    
    // Save Profile Simulation
    const saveProfileBtn = document.getElementById('saveProfileBtn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-check-lg"></i> Saved Successfully';
                this.classList.replace('btn-primary', 'btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.disabled = false;
                    this.classList.replace('btn-success', 'btn-primary');
                }, 2000);
            }, 1000);
        });
    }

    // Settings Navigation Logic
    const settingsNavLinks = document.querySelectorAll('.settings-nav .nav-link');
    const settingsSections = document.querySelectorAll('.settings-section');

    settingsNavLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active classes
            settingsNavLinks.forEach(l => l.classList.remove('active'));
            settingsSections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked
            this.classList.add('active');
            
            // Show corresponding section
            const targetId = this.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Theme Selection Logic
    const themeBoxes = document.querySelectorAll('.theme-box');
    themeBoxes.forEach(box => {
        box.addEventListener('click', function() {
            themeBoxes.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Simulated visual feedback for dark mode toggle UI only
            // Real implementation would swap a CSS variable or class on <body>
        });
    });

    // Delete Account Mock
    const btnDelete = document.getElementById('btnDeleteAccount');
    if(btnDelete) {
        btnDelete.addEventListener('click', () => {
            const confirmed = confirm("Are you sure you want to permanently delete your PlacementPrep AI account? This action cannot be undone.");
            if(confirmed) {
                alert("Account Deletion request submitted. Your session will be terminated.");
            }
        });
    }

    // Skill Tag Remove logic
    const skillRemoves = document.querySelectorAll('.skill-tag-edit i');
    skillRemoves.forEach(icon => {
        icon.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });

});
