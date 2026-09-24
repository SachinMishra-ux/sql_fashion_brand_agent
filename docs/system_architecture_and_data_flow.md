# 🏛️ End-to-End System Architecture & Deployment Pipeline
### Comprehensive Visual Architecture for Maison Luxé AI Stylist (STELLA)

---

## 🎯 1. Complete End-to-End Visual Architecture

```text
========================================================================================================================
                                      STAGE 1: LOCAL DEVELOPMENT & CI/CD PIPELINE
========================================================================================================================

  ┌─────────────────────────┐
  │  💻 Local Workstation   │
  │  • FastAPI Backend Code │
  │  • Next/Nginx Frontend  │
  │  • Task Definitions     │
  └────────────┬────────────┘
               │  (1) git push origin main
               ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  🐙 GitHub Repository & Actions CI/CD Pipeline                                                                   │
  │                                                                                                                  │
  │   [ 1. Test & Lint ] ──▶ [ 2. Docker Build ] ──▶ [ 3. AWS ECR Push ] ──▶ [ 4. Deploy to ECS Fargate ]            │
  │   • Pytest Unit Tests     • Build Frontend Image  • Push frontend:latest  • Register new Task Def Revision       │
  │   • Ruff Code Linting     • Build Backend Image   • Push backend:latest   • Trigger Zero-Downtime Rolling Update │
  └────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                           │
                                                           │ (2) Automated Deployment via IAM Credentials
                                                           ▼
========================================================================================================================
                                       STAGE 2: AWS CLOUD INFRASTRUCTURE (VPC)
========================================================================================================================

  ┌─────────────────────────────────────────┐           ┌─────────────────────────────────────────┐
  │  🌐 GoDaddy Registrar                   │           │  🔒 AWS Certificate Manager (ACM)       │
  │  • Domain: predictoraa.com              │           │  • Free Auto-Renewing SSL/TLS Cert      │
  │  • Nameservers delegated to Route 53    │           │  • Wildcard: *.predictoraa.com          │
  └────────────────────┬────────────────────┘           └────────────────────┬────────────────────┘
                       │                                                     │
                       ▼                                                     ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  🗺️ Amazon Route 53 (DNS Hosted Zone: predictoraa.com)                                                            │
  │  • A Record (Alias): predictoraa.com      ──▶ Application Load Balancer (ALB)                                    │
  │  • A Record (Alias): www.predictoraa.com  ──▶ Application Load Balancer (ALB)                                    │
  └────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                           │
                                                           │ (3) User Traffic (HTTP / HTTPS)
                                                           ▼
  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │  ⚖️ Application Load Balancer (ALB: alb-fashion-agent) [Security Group: alb-sg (Ports 80, 443)]                   │
  │                                                                                                                  │
  │   ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
  │   │  Listener Port 80 (HTTP)  ──▶ HTTP 301 Redirect to HTTPS (Port 443)                                     │   │
  │   └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
  │   ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
  │   │  Listener Port 443 (HTTPS) [ACM SSL Certificate: predictoraa.com]                                        │   │
  │   │                                                                                                          │   │
  │   │  ├── Path Rule 1: /chat*, /products*, /health*, /auth* ──▶ [ Target Group: tg-fashion-backend (Port 8000) ] │   │
  │   │  └── Default Rule: /*                                  ──▶ [ Target Group: tg-fashion-frontend (Port 80) ]   │   │
  │   └──────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
  └──────────────────────────────────┬──────────────────────────────────────────┬────────────────────────────────────┘
                                     │                                          │
                                     │ Forward Frontend Traffic                 │ Forward Backend API Traffic
                                     ▼                                          ▼
========================================================================================================================
                     STAGE 3: SERVERLESS COMPUTE (AMAZON ECS CLUSTER: fashion-agent-cluster)
========================================================================================================================

  ┌───────────────────────────────────────────────────┐      ┌───────────────────────────────────────────────────────┐
  │  🌐 Service: fashion-frontend-service             │      │  ⚙️ Service: fashion-backend-service                  │
  │  [Security Group: ecs-tasks-sg (Port 80 from ALB)]│      │  [Security Group: ecs-tasks-sg (Port 8000 from ALB)]  │
  │                                                   │      │                                                       │
  │   ┌───────────────────────────────────────────┐   │      │   ┌───────────────────────────────────────────────┐   │
  │   │  🚀 Fargate Task (MicroVM)                │   │      │   │  🚀 Fargate Task (MicroVM)                    │   │
  │   │  • Sizing: 0.25 vCPU · 512 MB RAM         │   │      │   │  • Sizing: 0.5 vCPU · 1024 MB RAM             │   │
  │   │  • Dedicated ENI Private IP in VPC        │   │      │   │  • Dedicated ENI Private IP in VPC            │   │
  │   │                                           │   │      │   │                                               │   │
  │   │   🐳 Nginx Alpine Container (Port 80)     │   │      │   │   🐳 FastAPI Container (Port 8000)            │   │
  │   │   • Serves: HTML, CSS, JavaScript, Assets │   │      │   │   • Runs: STELLA LangChain AI Agent           │   │
  │   └───────────────────────────────────────────┘   │      │   │   • Uvicorn ASGI Server with Multi-Workers    │   │
  └───────────────────────────────────────────────────┘      │   └───────────────────────┬───────────────────────┘   │
                                                             └───────────────────────────┼───────────────────────────┘
                                                                                         │
                                     ┌───────────────────────────────────────────────────┴────────────────┐
                                     │ (Outbound queries over Internet Gateway)                          │
                                     ▼                                                                    ▼
========================================================================================================================
                                STAGE 4: EXTERNAL CLOUD DATABASES & AI SERVICES
========================================================================================================================

  ┌─────────────────────────────────────────┐  ┌─────────────────────────────────────────┐  ┌────────────────────────┐
  │  🗄️ Aiven Cloud (MySQL)                 │  │  🐘 Supabase (PostgreSQL Pooler)        │  │  🤖 SenseNova AI API   │
  │  • Host: mysql-*.aivencloud.com         │  │  • Host: aws-0-*.pooler.supabase.com    │  │  • Chat Completion    │
  │  • Port: 16512 (TLS Encrypted)          │  │  • Port: 5432 (IPv4 Connection Pooler)  │  │  • SQL Agent Reasoning │
  │  • Tables: Products, Inventory, Orders  │  │  • Tables: Conversation Checkpoints     │  │  • Styling Suggestions │
  └─────────────────────────────────────────┘  └─────────────────────────────────────────┘  └────────────────────────┘

========================================================================================================================
                              STAGE 5: AWS SUPPORTING & SECURITY SERVICES
========================================================================================================================

  ┌─────────────────────────────────────────┐  ┌─────────────────────────────────────────┐  ┌────────────────────────┐
  │  📦 Amazon ECR (Private Registries)     │  │  🔐 AWS SSM Parameter Store             │  │  🪵 AWS CloudWatch Logs │
  │  • fashion-frontend:latest              │  │  • /fashion-agent/MYSQL_PASSWORD        │  │  • /ecs/fashion-frontend   │
  │  • fashion-backend:latest               │  │  • /fashion-agent/POSTGRES_PASSWORD     │  │  • /ecs/fashion-backend    │
  │  • Image Vulnerability Scanning         │  │  • /fashion-agent/SENSENOVA_API_KEY     │  │  • 30-Day Retention Policy │
  └─────────────────────────────────────────┘  └─────────────────────────────────────────┘  └────────────────────────┘
```

---

## 🔄 2. Detailed Flow Breakdown: Step-by-Step

### Phase 1: Local Code to GitHub Actions (CI/CD)
1. **Local Development**: The developer writes code locally and executes `git push origin main`.
2. **GitHub Actions Trigger**: A webhook triggers `.github/workflows/deploy.yml`.
3. **CI Pipeline (Test & Quality)**:
   - Sets up Python 3.12.
   - Runs `ruff` for code linting and formatting standards.
   - Runs `pytest` to ensure all agent tools and database models pass unit tests.
4. **CD Pipeline (Docker Build & Registry Push)**:
   - Logs into Amazon ECR using AWS credentials stored in GitHub Secrets.
   - Builds the lightweight Nginx Frontend Docker image and tags it as `fashion-frontend:latest`.
   - Builds the Python FastAPI Backend Docker image and tags it as `fashion-backend:latest`.
   - Pushes both images securely into private Amazon ECR repositories.
5. **ECS Deployment**:
   - Renders updated Task Definitions (`deploy/ecs-backend-task.json` and `deploy/ecs-frontend-task.json`).
   - Registers new revisions (`:2`, `:3`, etc.) in AWS ECS.
   - Instructs ECS Services to perform a zero-downtime rolling deployment.

---

### Phase 2: DNS & SSL Routing Layer
1. **User Request**: A shopper visits `https://predictoraa.com` in their web browser.
2. **GoDaddy Delegation**: GoDaddy delegates DNS authority to the 4 AWS Route 53 Name Servers (`awsdns-*`).
3. **Route 53 Resolution**: Route 53 evaluates the `A (Alias)` record and resolves the domain directly to the AWS Application Load Balancer (ALB) DNS name without extra DNS lookup latency.
4. **AWS Certificate Manager (ACM)**: Terminates SSL/TLS encryption at the Load Balancer with the wildcard certificate `*.predictoraa.com`.

---

### Phase 3: Application Load Balancer (ALB) Routing Engine
The ALB acts as the single public gateway into your VPC, isolating your containers:

```text
Incoming HTTPS Request on Port 443
               │
               ├── Path matches /chat, /products, /health, /auth?
               │     │
               │     └──▶ YES ──▶ Forward to tg-fashion-backend ──▶ FastAPI Container (Port 8000)
               │
               └── Path is anything else (/*)?
                     │
                     └──▶ Forward to tg-fashion-frontend ──▶ Nginx Container (Port 80)
```

* **Security Policy**: The ALB Security Group (`alb-sg`) accepts public traffic on ports `80` and `443`.
* **Container Protection**: The ECS Tasks Security Group (`ecs-tasks-sg`) **only** accepts incoming traffic originating from `alb-sg`, preventing direct internet attacks on containers.

---

### Phase 4: AWS ECS Fargate Execution Engine
1. **Serverless MicroVMs**: AWS Fargate allocates dedicated, isolated compute capacity for each container task without managing EC2 instances.
2. **Secret Injection**: During container boot, AWS ECS assumes the `ecsTaskExecutionRole` and fetches encrypted database passwords and API keys from **AWS SSM Parameter Store**, injecting them directly into container memory as environment variables.
3. **Frontend Task**: Nginx serves the single-page application (`index.html`, `style.css`, `app.js`) with HTTP caching, gzip compression, and ultra-fast static file response times.
4. **Backend Task**: FastAPI processes natural language user queries, invokes LangChain agents, executes SQL queries, and streams responses back.
5. **Real-Time Logging**: Both containers automatically forward all `stdout` and `stderr` logs to **CloudWatch Logs** (`/ecs/fashion-frontend` and `/ecs/fashion-backend`).

---

### Phase 5: External Database & AI Communications
1. **Aiven Cloud MySQL (Port 16512)**: The backend securely executes read/write queries against MySQL for catalog exploration, stock validation, and order management.
2. **Supabase PostgreSQL (Port 5432)**: Uses an IPv4 connection pooler to persist multi-turn chat memory and session state across user interactions.
3. **SenseNova LLM API (HTTPS)**: Provides advanced reasoning, intent extraction, SQL generation, and luxury fashion styling recommendations.

---

## 📊 Summary of Architectural Components

| Component | AWS / Cloud Service | Function / Responsibility |
| :--- | :--- | :--- |
| **Domain Registrar** | GoDaddy | Owns `predictoraa.com` domain registration. |
| **DNS Management** | AWS Route 53 | Resolves domain apex and subdomains via ALB Aliases. |
| **SSL / TLS Encryption** | AWS ACM | Provides free, auto-renewing HTTPS certificate. |
| **Load Balancer** | AWS Application Load Balancer | Routes traffic via path rules & terminates SSL. |
| **Container Registry** | AWS ECR | Private storage for Docker images. |
| **Serverless Compute** | AWS ECS (Fargate) | Runs isolated container MicroVMs on demand. |
| **Secrets Management** | AWS SSM Parameter Store | Encrypted storage for DB passwords & API keys. |
| **Observability** | AWS CloudWatch | Centralized log streaming and container health monitoring. |
| **Transactional DB** | Aiven Cloud MySQL | E-commerce product catalog & customer accounts. |
| **Session State DB** | Supabase PostgreSQL | Chat history and agent checkpoint storage. |
| **AI Inference** | SenseNova LLM | Natural language understanding and styling intelligence. |
| **CI/CD Automation** | GitHub Actions | Automated linting, testing, Docker build & ECS rollout. |
