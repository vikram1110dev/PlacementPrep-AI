-- PlacementPrep AI Complete MySQL Schema
-- Generated for FastAPI & SQLAlchemy Architecture

SET FOREIGN_KEY_CHECKS=0;

-- ========================================================
-- 1. AUTHENTICATION & ACCESS CONTROL
-- ========================================================

CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'ADMIN', 'STUDENT', 'MENTOR'
    description TEXT
);

CREATE TABLE user_roles (
    user_id CHAR(36) NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'edit_users', 'view_analytics'
    module VARCHAR(50) NOT NULL
);

CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

CREATE TABLE refresh_tokens (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    token VARCHAR(512) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token)
);

CREATE TABLE otp_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    type ENUM('EMAIL_VERIFICATION', 'PASSWORD_RESET') NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE sessions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    device_info VARCHAR(255),
    ip_address VARCHAR(45),
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================================
-- 2. STUDENT MODULE
-- ========================================================

CREATE TABLE student_profiles (
    user_id CHAR(36) PRIMARY KEY,
    phone_number VARCHAR(20),
    dob DATE,
    gender ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY'),
    location VARCHAR(100),
    bio TEXT,
    github_url VARCHAR(255),
    linkedin_url VARCHAR(255),
    leetcode_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    placement_score INT DEFAULT 0,
    current_xp INT DEFAULT 0,
    level INT DEFAULT 1,
    streak_days INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE education (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    degree VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    start_year INT,
    end_year INT,
    cgpa DECIMAL(4,2),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    category ENUM('TECHNICAL', 'SOFT', 'TOOL') NOT NULL
);

CREATE TABLE student_skills (
    user_id CHAR(36) NOT NULL,
    skill_id INT NOT NULL,
    proficiency ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'BEGINNER',
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    issuer VARCHAR(100) NOT NULL,
    issue_date DATE,
    credential_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date_achieved DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE student_preferences (
    user_id CHAR(36) PRIMARY KEY,
    job_roles JSON, -- Target job roles
    preferred_locations JSON,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    theme ENUM('LIGHT', 'DARK', 'SYSTEM') DEFAULT 'SYSTEM',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================================
-- 3. LEARNING MODULE (Courses & Resources)
-- ========================================================

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(255),
    created_by CHAR(36) NULL, -- Admin/Mentor who created it
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_type ENUM('VIDEO', 'ARTICLE', 'QUIZ') NOT NULL,
    content_url VARCHAR(255),
    text_content TEXT,
    order_index INT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
);

CREATE TABLE user_progress (
    user_id CHAR(36) NOT NULL,
    topic_id INT NOT NULL,
    status ENUM('IN_PROGRESS', 'COMPLETED') DEFAULT 'IN_PROGRESS',
    completed_at TIMESTAMP NULL,
    PRIMARY KEY (user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    topic_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- ========================================================
-- 4. APTITUDE MODULE
-- ========================================================

CREATE TABLE aptitude_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL -- e.g., 'Quantitative', 'Logical'
);

CREATE TABLE aptitude_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL, -- e.g., 'Time and Work'
    FOREIGN KEY (category_id) REFERENCES aptitude_categories(id) ON DELETE CASCADE
);

CREATE TABLE aptitude_questions (
    id CHAR(36) PRIMARY KEY,
    topic_id INT NOT NULL,
    question_text TEXT NOT NULL,
    difficulty ENUM('EASY', 'MEDIUM', 'HARD') NOT NULL,
    explanation TEXT,
    FOREIGN KEY (topic_id) REFERENCES aptitude_topics(id) ON DELETE CASCADE
);

CREATE TABLE aptitude_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id CHAR(36) NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES aptitude_questions(id) ON DELETE CASCADE
);

CREATE TABLE aptitude_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    question_id CHAR(36) NOT NULL,
    selected_option_id INT,
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds INT,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES aptitude_questions(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_option_id) REFERENCES aptitude_options(id) ON DELETE SET NULL
);

-- ========================================================
-- 5 & 6. DSA & CODING MODULE
-- ========================================================

CREATE TABLE coding_problems (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    input_format TEXT,
    output_format TEXT,
    constraints TEXT,
    difficulty ENUM('EASY', 'MEDIUM', 'HARD') NOT NULL,
    category VARCHAR(100), -- e.g., Arrays, Trees, Dynamic Programming
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    problem_id CHAR(36) NOT NULL,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (problem_id) REFERENCES coding_problems(id) ON DELETE CASCADE
);

CREATE TABLE compiler_languages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'Python', 'Java', 'C++'
    version VARCHAR(20) NOT NULL,
    template_code TEXT
);

CREATE TABLE coding_submissions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    problem_id CHAR(36) NOT NULL,
    language_id INT NOT NULL,
    source_code TEXT NOT NULL,
    status ENUM('ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED', 'COMPILATION_ERROR', 'RUNTIME_ERROR') NOT NULL,
    execution_time_ms INT,
    memory_used_kb INT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES coding_problems(id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES compiler_languages(id) ON DELETE CASCADE,
    INDEX idx_user_problem (user_id, problem_id)
);

CREATE TABLE leaderboards (
    user_id CHAR(36) PRIMARY KEY,
    score INT DEFAULT 0,
    problems_solved INT DEFAULT 0,
    global_rank INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================================
-- 7. PROJECTS PORTFOLIO
-- ========================================================

CREATE TABLE project_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL -- e.g., 'Web Dev', 'AI/ML'
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') NOT NULL,
    estimated_hours INT,
    github_repo_template VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES project_categories(id) ON DELETE CASCADE
);

CREATE TABLE user_projects (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    project_id INT NOT NULL,
    status ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'REVIEW_PENDING') DEFAULT 'NOT_STARTED',
    github_link VARCHAR(255),
    live_link VARCHAR(255),
    feedback TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ========================================================
-- 8. COMPANY MODULE
-- ========================================================

CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    logo_url VARCHAR(255),
    description TEXT,
    industry VARCHAR(100),
    company_type ENUM('PRODUCT', 'SERVICE', 'STARTUP') NOT NULL
);

CREATE TABLE company_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(100) NOT NULL, -- e.g., 'SDE 1', 'Data Analyst'
    avg_package_lpa DECIMAL(5,2),
    eligibility_criteria TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE company_hiring_processes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    round_number INT NOT NULL,
    round_name VARCHAR(100) NOT NULL, -- e.g., 'Online Assessment', 'Technical HR'
    description TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Bridge table associating Coding Problems to Companies
CREATE TABLE company_coding_problems (
    company_id INT NOT NULL,
    problem_id CHAR(36) NOT NULL,
    PRIMARY KEY (company_id, problem_id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES coding_problems(id) ON DELETE CASCADE
);

-- ========================================================
-- 9. AI MENTOR MODULE
-- ========================================================

CREATE TABLE ai_chat_sessions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    title VARCHAR(255),
    context ENUM('GENERAL', 'CODING_HELP', 'MOCK_INTERVIEW', 'RESUME_REVIEW') DEFAULT 'GENERAL',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE ai_messages (
    id CHAR(36) PRIMARY KEY,
    session_id CHAR(36) NOT NULL,
    sender ENUM('USER', 'AI') NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_chat_sessions(id) ON DELETE CASCADE
);

-- ========================================================
-- 10. RESUME BUILDER MODULE
-- ========================================================

CREATE TABLE resume_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    thumbnail_url VARCHAR(255),
    html_structure TEXT,
    is_premium BOOLEAN DEFAULT FALSE
);

CREATE TABLE generated_resumes (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    template_id INT NOT NULL,
    resume_data JSON NOT NULL, -- Stores all fields filled by user
    ats_score INT DEFAULT 0,
    pdf_url VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES resume_templates(id) ON DELETE CASCADE
);

-- ========================================================
-- 11. ANALYTICS & LOGS
-- ========================================================

CREATE TABLE daily_activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    activity_date DATE NOT NULL,
    study_minutes INT DEFAULT 0,
    problems_solved INT DEFAULT 0,
    UNIQUE KEY uk_user_date (user_id, activity_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================================
-- 12. ADMIN & SYSTEM MODULE
-- ========================================================

CREATE TABLE notifications (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NULL, -- NULL means broadcast to all
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('SYSTEM', 'ALERT', 'ACHIEVEMENT') DEFAULT 'SYSTEM',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id CHAR(36) NOT NULL,
    action VARCHAR(255) NOT NULL,
    target_entity VARCHAR(100),
    target_id VARCHAR(100),
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE RESTRICT
);

SET FOREIGN_KEY_CHECKS=1;
