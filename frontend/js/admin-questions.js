document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://localhost:1111/api/v1/aptitude';
    const token = localStorage.getItem('token'); // Assuming admin logs in and stores token

    let questions = [];
    let currentFilters = { skip: 0, limit: 50, include_deleted: true };

    const tbody = document.querySelector('tbody');
    const searchInput = document.getElementById('searchInput');
    const difficultyFilter = document.getElementById('difficultyFilter');
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    async function fetchQuestions() {
        try {
            const params = new URLSearchParams(currentFilters);
            const res = await fetch(`${API_BASE}/questions?${params.toString()}`, { headers });
            if (!res.ok) throw new Error('Failed to fetch questions');
            const data = await res.json();
            questions = data.data;
            renderTable();
        } catch (err) {
            console.error(err);
        }
    }

    function renderTable() {
        if(!tbody) return;
        tbody.innerHTML = '';
        if(questions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No questions found.</td></tr>';
            return;
        }

        questions.forEach(q => {
            const tr = document.createElement('tr');
            if(q.deleted_at) {
                tr.classList.add('table-secondary', 'text-muted');
            }
            
            const badgeClass = q.difficulty === 'EASY' ? 'bg-success' : (q.difficulty === 'MEDIUM' ? 'bg-warning text-dark' : 'bg-danger');
            const activeStatus = q.is_active ? '<span class="badge bg-primary">Active</span>' : '<span class="badge bg-secondary">Inactive</span>';
            const deletedStatus = q.deleted_at ? '<span class="badge bg-dark">Deleted</span>' : '';
            
            tr.innerHTML = `
                <td>#${q.id.substring(0,6)}</td>
                <td><span class="fw-medium">${q.question_text.substring(0, 50)}${q.question_text.length > 50 ? '...' : ''}</span></td>
                <td>Topic ID: ${q.topic_id}</td>
                <td><span class="badge ${badgeClass}">${q.difficulty}</span></td>
                <td>${q.company || '-'}</td>
                <td>
                    ${activeStatus} ${deletedStatus}
                </td>
                <td>
                    <button class="btn btn-light btn-sm text-primary" onclick="editQuestion('${q.id}')"><i class="bi bi-pencil"></i></button>
                    ${q.deleted_at 
                        ? `<button class="btn btn-light btn-sm text-success" onclick="restoreQuestion('${q.id}')" title="Restore"><i class="bi bi-arrow-counterclockwise"></i></button>
                           <button class="btn btn-light btn-sm text-danger" onclick="hardDeleteQuestion('${q.id}')" title="Hard Delete"><i class="bi bi-trash-fill"></i></button>`
                        : `<button class="btn btn-light btn-sm text-warning" onclick="softDeleteQuestion('${q.id}')" title="Soft Delete"><i class="bi bi-trash"></i></button>`
                    }
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.editQuestion = (id) => {
        const q = questions.find(x => x.id === id);
        if(!q) return;
        
        document.getElementById('q_id').value = q.id;
        document.getElementById('q_topic_id').value = q.topic_id;
        document.getElementById('q_text').value = q.question_text;
        document.getElementById('q_difficulty').value = q.difficulty;
        document.getElementById('q_opt_a').value = q.option_a;
        document.getElementById('q_opt_b').value = q.option_b;
        document.getElementById('q_opt_c').value = q.option_c;
        document.getElementById('q_opt_d').value = q.option_d;
        document.getElementById('q_correct').value = q.correct_answer;
        document.getElementById('q_explanation').value = q.explanation || '';
        document.getElementById('q_company').value = q.company || '';
        document.getElementById('q_tags').value = q.tags || '';
        document.getElementById('q_marks').value = q.marks;
        document.getElementById('q_time').value = q.estimated_time_seconds;
        
        document.getElementById('questionModalLabel').innerText = "Edit Question";
        new bootstrap.Modal(document.getElementById('questionModal')).show();
    };

    window.softDeleteQuestion = async (id) => {
        if(!confirm("Soft delete this question?")) return;
        try {
            await fetch(`${API_BASE}/questions/${id}`, { method: 'DELETE', headers });
            fetchQuestions();
        } catch(e) { console.error(e); }
    };
    
    window.hardDeleteQuestion = async (id) => {
        if(!confirm("Permanently delete this question? This cannot be undone.")) return;
        try {
            await fetch(`${API_BASE}/questions/${id}/hard`, { method: 'DELETE', headers });
            fetchQuestions();
        } catch(e) { console.error(e); }
    };
    
    window.restoreQuestion = async (id) => {
        try {
            await fetch(`${API_BASE}/questions/${id}/restore`, { method: 'PATCH', headers });
            fetchQuestions();
        } catch(e) { console.error(e); }
    };

    if(document.getElementById('questionForm')) {
        document.getElementById('questionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('q_id').value;
            const payload = {
                topic_id: parseInt(document.getElementById('q_topic_id').value),
                question_text: document.getElementById('q_text').value,
                difficulty: document.getElementById('q_difficulty').value,
                option_a: document.getElementById('q_opt_a').value,
                option_b: document.getElementById('q_opt_b').value,
                option_c: document.getElementById('q_opt_c').value,
                option_d: document.getElementById('q_opt_d').value,
                correct_answer: document.getElementById('q_correct').value,
                explanation: document.getElementById('q_explanation').value,
                company: document.getElementById('q_company').value,
                tags: document.getElementById('q_tags').value,
                marks: parseInt(document.getElementById('q_marks').value) || 1,
                estimated_time_seconds: parseInt(document.getElementById('q_time').value) || 60
            };

            const method = id ? 'PUT' : 'POST';
            const url = id ? `${API_BASE}/questions/${id}` : `${API_BASE}/questions`;

            try {
                const res = await fetch(url, { method, headers, body: JSON.stringify(payload) });
                if(res.ok) {
                    bootstrap.Modal.getInstance(document.getElementById('questionModal')).hide();
                    fetchQuestions();
                } else {
                    const data = await res.json();
                    alert("Error: " + JSON.stringify(data.detail || data.message));
                }
            } catch(e) {
                console.error(e);
            }
        });
    }

    if(document.getElementById('btnAddQuestion')) {
        document.getElementById('btnAddQuestion').addEventListener('click', () => {
            document.getElementById('questionForm').reset();
            document.getElementById('q_id').value = '';
            document.getElementById('questionModalLabel').innerText = "Add Question";
            new bootstrap.Modal(document.getElementById('questionModal')).show();
        });
    }

    const applyFilters = () => {
        currentFilters = { skip: 0, limit: 50, include_deleted: true };
        if(searchInput && searchInput.value.trim()) currentFilters.search = searchInput.value.trim();
        if(difficultyFilter && difficultyFilter.value) currentFilters.difficulty = difficultyFilter.value;
        fetchQuestions();
    };

    if(searchInput) {
        searchInput.addEventListener('input', () => { clearTimeout(window.searchTimeout); window.searchTimeout = setTimeout(applyFilters, 500); });
    }
    if(difficultyFilter) {
        difficultyFilter.addEventListener('change', applyFilters);
    }

    if(document.getElementById('btnExport')) {
        document.getElementById('btnExport').addEventListener('click', () => {
            window.open(`${API_BASE}/questions/export?include_deleted=false`);
        });
    }

    if(document.getElementById('btnImport')) {
        document.getElementById('btnImport').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('importModal')).show();
        });
    }

    if(document.getElementById('importForm')) {
        document.getElementById('importForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('importFile');
            if(!fileInput.files.length) return;
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            try {
                const res = await fetch(`${API_BASE}/questions/import`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
                const data = await res.json();
                if(res.ok && data.success) {
                    alert(data.message);
                    bootstrap.Modal.getInstance(document.getElementById('importModal')).hide();
                    fetchQuestions();
                } else {
                    alert("Import failed:\n" + (data.data?.errors?.join('\n') || data.message));
                }
            } catch(e) {
                console.error(e);
                alert("Import failed");
            }
        });
    }

    fetchQuestions();
});
