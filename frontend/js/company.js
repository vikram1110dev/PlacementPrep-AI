document.addEventListener('DOMContentLoaded', () => {
    // Check Auth
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const API_URL = '/api/v1/companies';

    // DOM Elements
    const listView = document.getElementById('companyListView');
    const detailsView = document.getElementById('companyDetailsView');
    const companiesGrid = document.getElementById('companiesGrid');
    const backBtn = document.getElementById('backToCompaniesBtn');

    // Details DOM Elements
    const detailsCompanyLogo = document.getElementById('detailsCompanyLogo');
    const detailsCompanyTitle = document.getElementById('detailsCompanyTitle');
    const detailsCompanyName = document.getElementById('detailsCompanyName');
    const detailsCompanyIndustry = document.getElementById('detailsCompanyIndustry');
    const detailsCompanyTier = document.getElementById('detailsCompanyTier');
    const statAvgPackage = document.getElementById('statAvgPackage');
    const statCompetition = document.getElementById('statCompetition');
    const statSuccessRate = document.getElementById('statSuccessRate');
    const statHiringMode = document.getElementById('statHiringMode');
    const companyMockTests = document.getElementById('companyMockTests');

    let allCompanies = [];

    // Fetch Companies
    async function fetchCompanies() {
        try {
            const res = await fetch(API_URL, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                allCompanies = data.data;
                renderCompanies(allCompanies);
            }
        } catch (error) {
            console.error('Error fetching companies:', error);
            companiesGrid.innerHTML = '<div class="text-danger w-100 text-center">Failed to load companies.</div>';
        }
    }

    function renderCompanies(companies) {
        companiesGrid.innerHTML = '';
        if (companies.length === 0) {
            companiesGrid.innerHTML = '<div class="text-muted w-100 text-center">No companies found.</div>';
            return;
        }

        companies.forEach(comp => {
            const isDream = comp.tier === 'Dream';
            const html = `
                <div class="company-card" style="cursor:pointer;" onclick="openCompanyDetails(${comp.id})">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="company-logo" style="background-color: #2563EB;">
                            <img src="${comp.logo_url}" alt="${comp.name}" style="width:100%; border-radius:12px;">
                        </div>
                        ${isDream ? '<span class="badge bg-warning text-dark"><i class="bi bi-star-fill me-1"></i> Dream</span>' : ''}
                    </div>
                    <h5 class="fw-bold mb-1">${comp.name}</h5>
                    <p class="text-muted small mb-3">${comp.industry_type || 'Unknown'} • ${comp.description || ''}</p>
                    <button class="btn btn-outline-primary w-100 rounded-pill btn-sm">View Roadmap</button>
                </div>
            `;
            companiesGrid.innerHTML += html;
        });
    }

    // Expose to global scope for onclick handler
    window.openCompanyDetails = async function(companyId) {
        // Show loading state...
        listView.classList.add('d-none');
        detailsView.classList.remove('d-none');
        
        try {
            const res = await fetch(`${API_URL}/${companyId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                populateCompanyDetails(data.data);
            }
        } catch(error) {
            console.error('Error loading details:', error);
        }
    };

    function populateCompanyDetails(comp) {
        detailsCompanyLogo.innerHTML = `<img src="${comp.logo_url}" style="width:100%; height:100%; border-radius:12px;">`;
        detailsCompanyTitle.textContent = `${comp.name} Preparation Hub`;
        detailsCompanyName.textContent = comp.name;
        detailsCompanyIndustry.textContent = comp.industry_type || 'Industry';
        detailsCompanyTier.textContent = comp.tier || 'Standard';

        // Stats
        const s = comp.stats || {};
        statAvgPackage.textContent = s.avg_package || 'N/A';
        statCompetition.textContent = s.competition_level || 'N/A';
        statSuccessRate.textContent = s.success_rate_percent ? `${s.success_rate_percent}%` : 'N/A';
        statHiringMode.textContent = s.hiring_mode || 'N/A';

        // Mock Tests
        companyMockTests.innerHTML = '';
        if (comp.patterns && comp.patterns.length > 0) {
            comp.patterns.forEach(pat => {
                const html = `
                    <div class="mock-card bg-light mb-3">
                        <h6 class="fw-bold mb-2">${comp.name} OA Mock - ${pat.role_name}</h6>
                        <div class="d-flex justify-content-between text-muted small fw-medium mb-3">
                            <span>${pat.total_questions} Questions</span>
                            <span>${pat.duration_minutes} Mins</span>
                        </div>
                        <button class="btn btn-primary w-100 rounded-pill btn-sm" onclick="startCompanyTest(${comp.id}, ${pat.id})">Start Test</button>
                    </div>
                `;
                companyMockTests.innerHTML += html;
            });
        } else {
            companyMockTests.innerHTML = '<p class="text-muted small">No mock tests available for this company yet.</p>';
        }
    }

    window.startCompanyTest = async function(companyId, patternId) {
        try {
            const res = await fetch(`${API_URL}/${companyId}/test/start`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pattern_id: patternId })
            });
            const data = await res.json();
            if (data.success && data.data.session_id) {
                // Navigate to test engine
                window.location.href = `aptitude-test.html?session_id=${data.data.session_id}&company_id=${companyId}`;
            } else {
                alert(data.message || 'Could not start test. Check console for details.');
            }
        } catch (error) {
            console.error('Error starting test:', error);
            alert('Failed to start test.');
        }
    };

    backBtn.addEventListener('click', () => {
        detailsView.classList.add('d-none');
        listView.classList.remove('d-none');
    });

    // Sidebar toggle for mobile
    document.getElementById('sidebarToggleBtn').addEventListener('click', () => {
        document.getElementById('sidebar').classList.add('show');
        document.getElementById('sidebarOverlay').classList.add('show');
    });

    document.getElementById('sidebarOverlay').addEventListener('click', () => {
        document.getElementById('sidebar').classList.remove('show');
        document.getElementById('sidebarOverlay').classList.remove('show');
    });

    // Init
    fetchCompanies();
});
