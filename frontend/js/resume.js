document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Zoom Controls
    const zoomInBtn = document.getElementById('zoomInBtn');
    const zoomOutBtn = document.getElementById('zoomOutBtn');
    const zoomResetBtn = document.getElementById('zoomResetBtn');
    const resumePaper = document.getElementById('resumePaper');
    
    let currentScale = 0.7; // Default scale to fit screen

    function applyZoom() {
        if(resumePaper) {
            resumePaper.style.transform = `scale(${currentScale})`;
        }
    }

    // Initial Zoom
    applyZoom();

    if(zoomInBtn) zoomInBtn.addEventListener('click', () => { currentScale += 0.1; applyZoom(); });
    if(zoomOutBtn) zoomOutBtn.addEventListener('click', () => { currentScale = Math.max(0.3, currentScale - 0.1); applyZoom(); });
    if(zoomResetBtn) zoomResetBtn.addEventListener('click', () => { currentScale = 0.7; applyZoom(); });

    // 2. Real-time Preview Binding
    const binds = [
        { inputId: 'inpName', targetId: 'resName' },
        { inputId: 'inpEmail', targetId: 'resEmail', prefix: 'Email: ' },
        { inputId: 'inpPhone', targetId: 'resPhone', prefix: 'Phone: ' },
        { inputId: 'inpLinkedin', targetId: 'resLinkedin', prefix: 'LinkedIn: ' },
        { inputId: 'inpSummary', targetId: 'resSummary' },
    ];

    binds.forEach(bind => {
        const input = document.getElementById(bind.inputId);
        const target = document.getElementById(bind.targetId);
        if(input && target) {
            input.addEventListener('input', function() {
                let val = this.value.trim();
                if(bind.prefix && val) val = bind.prefix + val;
                target.textContent = val || (this.placeholder || '');
            });
        }
    });

    // 3. AI Assistant Actions
    const aiBtns = document.querySelectorAll('.ai-generate-btn');
    aiBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-check-circle"></i> Applied';
                this.classList.replace('btn-outline-primary', 'btn-success');
                this.classList.replace('text-primary', 'text-white');
                
                // Simulate updating a field
                if(this.id === 'btnGenSummary') {
                    const summaryInput = document.getElementById('inpSummary');
                    if(summaryInput) {
                        summaryInput.value = "Highly motivated and detail-oriented Computer Science student with a strong foundation in Data Structures, Algorithms, and Full-Stack Development. Proven ability to build scalable web applications and eager to contribute to innovative projects.";
                        // Dispatch input event to update preview
                        summaryInput.dispatchEvent(new Event('input'));
                    }
                }
                
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.disabled = false;
                    this.classList.replace('btn-success', 'btn-outline-primary');
                    this.classList.replace('text-white', 'text-primary');
                }, 2000);
            }, 1500);
        });
    });

    // 4. Download PDF using html2pdf
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', function() {
            if (typeof html2pdf === 'undefined') {
                alert('html2pdf library is not loaded.');
                return;
            }
            
            const originalHTML = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating PDF...';
            this.disabled = true;

            const element = document.getElementById('resumePaper');
            
            // Temporarily reset transform for clean render
            const oldTransform = element.style.transform;
            element.style.transform = 'scale(1)';

            var opt = {
                margin:       0,
                filename:     'My_Resume.pdf',
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2 },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };

            html2pdf().set(opt).from(element).save().then(() => {
                this.innerHTML = '<i class="bi bi-check-lg"></i> Downloaded';
                element.style.transform = oldTransform;
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.disabled = false;
                }, 2000);
            });
        });
    }

    // 5. Template Selection
    const templates = document.querySelectorAll('.template-card');
    templates.forEach(t => {
        t.addEventListener('click', function() {
            templates.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            // Logic to swap CSS theme of the resume paper would go here
        });
    });

    // 6. ATS Score Analysis
    const atsBtn = document.getElementById('analyzeAtsBtn');
    if(atsBtn) {
        atsBtn.addEventListener('click', function() {
            const resultBox = document.getElementById('atsResult');
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Analyzing...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = 'Analyze Resume';
                this.disabled = false;
                resultBox.classList.remove('d-none');
            }, 1500);
        });
    }
});
