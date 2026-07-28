<h1 align="center">PlacementPrep AI 🚀</h1>

<p align="center">
  <strong>An Enterprise-Grade, AI-Powered Placement Preparation Platform</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python_3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
</p>

## 📝 Overview
**PlacementPrep AI** is a comprehensive, scalable, and intelligent platform designed to help students master Data Structures & Algorithms, practice Aptitude questions, generate ATS-friendly resumes, and receive real-time career guidance via an integrated Multi-Agent AI Mentor. 

Built using a modern microservices architecture with **Clean Architecture** principles, this project is designed to handle high concurrency and provide enterprise-level analytics for recruiters and admins.

## ✨ Core Features
- 🔐 **Advanced RBAC Authentication**: Secure JWT-based login with roles for Students, Mentors, Recruiters, and Super Admins.
- 🧑‍💻 **Interactive Coding Platform**: Built-in compiler and code execution engine (ready for Judge0 integration) for DSA practice.
- 🧠 **Multi-Agent AI Mentor**: Powered by LangGraph, ChromaDB (RAG), and Sentence Transformers to provide personalized career and interview guidance.
- 📄 **ATS-Optimized Resume Builder**: Dynamic resume generation and ATS scoring using python-docx and ReportLab.
- 📊 **Enterprise Admin CMS**: A highly optimized, Redis-cached admin dashboard for user tracking, analytics, and content management.
- 🐳 **Production-Ready DevOps**: Fully containerized using Docker, with automated CI/CD via GitHub Actions and Nginx reverse proxy configurations.

## 🛠️ Technology Stack
- **Backend**: FastAPI, Python 3.13+, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Database**: MySQL 8.0, Redis (Caching & Task Queues)
- **AI & RAG**: LangChain, LangGraph, ChromaDB, HuggingFace
- **Background Tasks**: Celery
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism UI), JavaScript
- **DevOps**: Docker, Docker Compose, Nginx, GitHub Actions

## 📂 Project Structure
```text
PlacementPrepAI/
│
├── backend/                  # FastAPI Application
│   ├── app/                  # Core Application Logic
│   │   ├── api/v1/           # API Routers (auth, admin, ai, resume, aptitude)
│   │   ├── models/           # SQLAlchemy Database Models
│   │   ├── schemas/          # Pydantic Validation Schemas
│   │   ├── repositories/     # Database Repository Layer
│   │   ├── services/         # Business Logic & AI Agents
│   │   └── core/             # Config, Security, and Logging
│   ├── infrastructure/       # Nginx & Monitoring configs
│   ├── .github/workflows/    # CI/CD Deployment Scripts
│   ├── docker-compose.yml    # Core Stack (API, DB, Redis, Celery)
│   └── Dockerfile            # Multi-stage production build
│
├── frontend/                 # UI Templates (HTML, CSS, JS)
│   ├── css/                  # Custom CSS (Variables, Components, Animations)
│   ├── js/                   # Vanilla JavaScript for API integration
│   └── pages/                # Dashboards, Resume Builder, Coding Editor
│
└── .gitignore
```

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following installed:
- [Docker & Docker Compose](https://www.docker.com/) (Ensure WSL2 is enabled on Windows)
- Git

### 2. Run Locally via Docker
Clone the repository and spin up the entire backend stack (FastAPI, MySQL, Redis, Celery) with a single command:
```bash
git clone https://github.com/vikram1110dev/PlacementPrep-AI.git
cd PlacementPrep-AI/backend

# Create your .env file
cp .env.example .env

# Build and start the containers
docker compose up -d --build
```
The backend API will be available at `http://localhost:8000`. You can view the automatic Swagger UI docs at `http://localhost:8000/docs`.

### 3. Running the Frontend
The frontend is pure HTML/CSS/JS. You can run it using a simple Python HTTP server:
```bash
cd ../frontend
python -m http.server 8080
```
Visit `http://localhost:8080` in your browser.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).

---
<p align="center">
  <i>Architected with ❤️ for placement preparation.</i>
</p>
