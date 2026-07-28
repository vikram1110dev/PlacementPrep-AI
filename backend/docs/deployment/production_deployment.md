# PlacementPrep AI - Production Deployment Guide

## Architecture Overview
The system is built on a containerized microservices architecture to ensure high availability and horizontal scalability.

### Core Stack (`docker-compose.yml`)
- **FastAPI**: Runs via Gunicorn + Uvicorn workers on port `8000`.
- **MySQL 8.0**: Persistent relational database.
- **Redis**: Used as a message broker for Celery and for caching (Dashboard metrics, LLM conversations).
- **Celery Worker**: Asynchronous background processor for long-running tasks like Judge0 code execution and AI generation.

### Monitoring Stack (`docker-compose.monitoring.yml`)
- **Prometheus**: Time-series metric scraper.
- **Grafana**: Visualization dashboard.
- **Loki & Promtail**: Docker log aggregation.

## Deployment Steps (Ubuntu 24.04 VPS)

### 1. Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose git -y
```

### 2. Clone the Repository
```bash
git clone https://github.com/yourorg/placementprep-ai.git /opt/placementprep
cd /opt/placementprep/backend
```

### 3. Environment Variables
Create a `.env` file in the `backend` directory.
```env
# Security
SECRET_KEY="super_secure_random_string"
ALGORITHM="HS256"

# Database
DATABASE_URL="mysql+pymysql://api_user:apipassword@db:3306/placementprep_ai"

# Redis
REDIS_HOST="redis"
REDIS_PORT=6379

# AI Models
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="AIza..."
```

### 4. Boot the Core Stack
```bash
docker-compose up -d --build
```
Check health status:
```bash
docker ps
curl http://localhost:8000/health
```

### 5. Nginx Reverse Proxy & SSL (Let's Encrypt)
Instead of exposing port `8000` directly, use the provided `nginx.conf` and secure it with Certbot.
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
sudo cp infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf
sudo systemctl restart nginx
sudo certbot --nginx -d api.placementprep.ai
```

## Scaling Guide
If the FastAPI endpoints begin to lag under heavy load:
1. Increase Gunicorn workers in the `Dockerfile` `CMD`: `--workers 8`.
2. Horizontally scale the API container using Docker Compose:
   ```bash
   docker-compose up -d --scale api=3
   ```
3. To handle more concurrent code executions or AI streams, scale the Celery workers:
   ```bash
   docker-compose up -d --scale celery_worker=5
   ```
