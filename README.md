# 👗 Maison Luxé — STELLA Autonomous AI Fashion Stylist & Retail Agent
### Production-Grade Full-Stack AI Agent with AWS ECS Fargate, LangChain, MySQL, PostgreSQL, and Automated GitHub Actions CI/CD

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github-actions)](https://github.com/SachinMishra-ux/sql_fashion_brand_agent/actions)
[![AWS Fargate](https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900?logo=amazon-aws)](https://aws.amazon.com/fargate/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Nginx](https://img.shields.io/badge/Frontend-Nginx%20Alpine-009639?logo=nginx)](https://nginx.org)
[![Domain](https://img.shields.io/badge/Live%20Domain-https%3A%2F%2Fpredictoraa.com-22C55E?logo=safari)](https://predictoraa.com)

---

## 🏛️ System Architecture Diagram

![Maison Luxé AWS Cloud Architecture](./docs/aws_architecture_diagram.png)

> 💡 *Vector SVG and High-Resolution 3840×2400 formats are available in [`docs/aws_architecture_diagram.svg`](./docs/aws_architecture_diagram.svg) and [`docs/aws_architecture_diagram.jpg`](./docs/aws_architecture_diagram.jpg).*  
> 🚀 **Live Interactive Architecture Visualizer:** Open [`docs/architecture_visualizer.html`](./docs/architecture_visualizer.html) in any browser for an interactive animated simulation of live traffic packets, ALB path routing, database calls, real-time client chat preview, and ECS auto-scaling!

### 🎬 Live Traffic Animation (`POST /chat` Flow)

Watch data packets move in real-time across the infrastructure when a customer queries the STELLA AI stylist:

![STELLA AI Production Traffic Flow](./docs/assets/architecture_chat_flow.gif)

*Trace Sequence: Client Browser &rarr; Route 53 DNS &rarr; ALB Path Match (`/chat*`) &rarr; ECS Fargate Backend (`:8000`) &rarr; SenseNova LLM (SQL Gen) &rarr; Aiven Cloud MySQL (Inventory) &rarr; Supabase Postgres (Checkpoints) &rarr; Client Response.*

### 📝 Handwritten Architecture Note & Sticky Notes

For an intuitive, whiteboard-style mental model, here is the complete end-to-end architecture captured as an engineer's handwritten notebook diagram with color-coded sticky notes:

![Maison Luxé Handwritten Architecture Notes](./docs/architecture_handwritten_notes.png)

*Components visualized: Client Browser (predictoraa.com) ➔ Route 53 DNS & ACM SSL ➔ AWS Application Load Balancer (ALB) ➔ AWS ECS Fargate Cluster (Frontend Nginx :80 & Backend FastAPI :8000) ➔ SenseNova LLM API ➔ Aiven Cloud MySQL ➔ Supabase PostgreSQL Memory.*

---

## 🌟 What is this Project All About?

**Maison Luxé** is a luxury digital fashion house featuring **STELLA** — an autonomous, conversational **AI Stylist & Retail Agent**. 

Unlike simple scripted chatbots, STELLA is an **autonomous LangChain Agent** powered by the **SenseNova LLM** that understands complex fashion aesthetics, dynamically queries real-time database inventory via SQL, applies tier-based customer VIP discounts, and remembers multi-turn conversational context.

### 🎯 Key Capabilities of STELLA:
1. **Curated Fashion Styling**: Analyzes natural language prompts (e.g., *"Show me luxury silk evening dresses under $600 with matching accessories"*), suggests complete cohesive outfits, and calculates VIP loyalty discounts.
2. **Real-Time SQL Database Querying**: Translates customer inquiries into safe, optimized SQL queries against a live **Aiven Cloud MySQL** database to inspect live stock, pricing, and sizing.
3. **Multi-Turn Persistent Chat Memory**: Checkpoints conversation history and user preferences into **Supabase PostgreSQL** via an IPv4 connection pooler, ensuring session state persists across reloads and device switches.
4. **JWT-Authenticated Customer Profiles**: Includes a 3-tier VIP customer profile switcher:
   - 👑 **Priya Sharma** (Platinum Member — 15% VIP Discount)
   - ⭐ **Aisha Khan** (Gold Member — 10% VIP Discount)
   - 💎 **Riya Verma** (Gold Member — 10% VIP Discount)
5. **Production Cloud Infrastructure**: Fully containerized and deployed on **AWS ECS Fargate (Serverless)** behind an **Application Load Balancer (ALB)**, secured with **AWS Certificate Manager (ACM)** wildcard SSL under **`https://predictoraa.com`**, and automated through **GitHub Actions CI/CD**.

---

## 🏗️ Technical Architecture & Cloud Layout

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     TRAFFIC & ROUTING LAYER                                       │
│                                                                                                   │
│  [ Client Browser ] ──▶ [ GoDaddy DNS ] ──▶ [ Amazon Route 53 ] ──▶ [ Application Load Balancer ] │
│                                                                        (HTTP 80 ➔ HTTPS 443)      │
└───────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                    │
                                                    ├── Path: /* (Default) ─────────▶ [ Nginx Frontend (Port 80) ]
                                                    └── Path: /chat*, /products* ───▶ [ FastAPI Backend (Port 8000) ]
                                                                                            │
                                                    ┌───────────────────────────────────────┴───────────────────────┐
                                                    │                   DATA & AI SERVICES LAYER                    │
                                                    │                                                               │
                                                    │  • Aiven Cloud MySQL: Products, Inventory, Orders             │
                                                    │  • Supabase PostgreSQL: Multi-Turn Conversation Memory        │
                                                    │  • SenseNova LLM: AI Reasoning & Natural Language Parsing     │
                                                    │  • LangSmith: Trace Observability & Token Analytics           │
                                                    └───────────────────────────────────────────────────────────────┘
```

---

## 📦 Microservices Breakdown

| Service | Technology | Port | Responsibilities |
| :--- | :--- | :---: | :--- |
| **Frontend** | Nginx Alpine / HTML5 / CSS3 / Vanilla JS | `80` | High-performance static asset delivery, responsive luxury UI, and dynamic profile switching. |
| **Backend API** | FastAPI / Python 3.12 / Uvicorn | `8000` | REST API, LangChain SQL Agent orchestration, JWT authentication, and health checks. |
| **Transactional DB** | Aiven Cloud MySQL | `16512` | Product catalog, real-time stock levels, category listings, and customer transaction logs. |
| **Session State DB** | Supabase PostgreSQL | `5432` | Thread-safe conversation checkpoints and agent memory storage. |
| **AI Inference** | SenseNova LLM | HTTPS | Intent classification, dynamic SQL generation, and high-fashion styling recommendations. |
| **Observability** | AWS CloudWatch & LangSmith | - | Real-time container log streaming (Live Tail) and end-to-end LLM execution tracing. |

---

## 🚀 GitHub Actions CI/CD Workflow

Every code change pushed to `main` triggers a zero-downtime rolling update on AWS:

```
git push origin main
        │
        ▼
[ 1. CI Stage: Code Quality ] ──▶ Runs Ruff linter & Pytest unit test suite
        │
        ▼
[ 2. Docker Multi-Stage Build ] ──▶ Builds `fashion-frontend` & `fashion-backend`
        │
        ▼
[ 3. Amazon ECR Push ] ──────────▶ Authenticates with AWS & pushes Docker image tags
        │
        ▼
[ 4. ECS Rolling Deployment ] ───▶ Deploys new Fargate Task Revision with zero downtime
```

---

## 🧪 Performance Testing & Auto-Scaling

The application is configured with **AWS Application Auto Scaling** based on **Target Tracking**:
* **Baseline**: 1 Task ($0.25 vCPU, 512 MB RAM) to minimize idle costs.
* **Auto-Scale Trigger**: When average CPU utilization exceeds **`70%`** for 60 seconds, ECS automatically scales up to **5 parallel containers**.
* **Scale-In Cooldown**: 300 seconds (5 minutes) to ensure traffic stability and prevent container flapping.

### Automated Load Testing Script:
Run a multi-threaded stress test simulating concurrent shoppers directly from the command line:

```bash
# Run with 5 concurrent users (dynamically loads tokens)
python3 scripts/stress_test.py --users 5
```

---

## 🛠️ Local Development Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/SachinMishra-ux/sql_fashion_brand_agent.git
cd sql_fashion_brand_agent
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables (`.env`)
Create a `.env` file in the project root:
```ini
# SenseNova AI API
SENSENOVA_API_KEY="your_sensenova_api_key"

# Aiven Cloud MySQL
MYSQL_HOST="your_aiven_mysql_host.aivencloud.com"
MYSQL_PORT="16512"
MYSQL_USER="avnadmin"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_DATABASE="defaultdb"

# Supabase PostgreSQL
POSTGRES_HOST="your_supabase_host.pooler.supabase.com"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres.your_project_ref"
POSTGRES_PASSWORD="your_supabase_password"
POSTGRES_DB="postgres"
POSTGRES_CONN_STR="postgresql://postgres.your_project_ref:password@host:5432/postgres"

# JWT Authentication
JWT_SECRET_KEY="your_secure_jwt_secret_key"
```

### 4. Run the Backend API Locally
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Run the Frontend
Open `frontend/index.html` in your browser or run a simple static server:
```bash
python3 -m http.server 8080 --directory frontend
```

---

## 📚 Documentation Index

All setup guides, runbooks, and educational resources are located in the [`docs/`](./docs/) directory:

| Document | Description | Format |
| :--- | :--- | :---: |
| 🎮 [**Interactive Architecture Visualizer**](./docs/architecture_visualizer.html) | Live animated traffic simulator showing ALB path routing, DB queries, and ECS auto-scaling. | [Interactive HTML](./docs/architecture_visualizer.html) |
| 📝 [**Handwritten Architecture Notes**](./docs/architecture_handwritten_notes.png) | Intuitive engineer notebook flat-lay sketch with sticky notes and hand-drawn cloud routing. | [PNG](./docs/architecture_handwritten_notes.png) · [JPG](./docs/architecture_handwritten_notes.jpg) |
| 🏛️ [**System Architecture & Data Flow**](./docs/system_architecture_and_data_flow.md) | Comprehensive visual guide detailing all AWS components & traffic flow. | Markdown |
| 🏆 [**Master Project Checklist & Roadmap**](./docs/master_project_checklist_and_roadmap.md) | Complete 8-stage project checklist from DB provisioning to LangSmith. | [Markdown](./docs/master_project_checklist_and_roadmap.md) · [PDF](./docs/master_project_checklist_and_roadmap.pdf) |
| 🧪 [**Stress Testing & Auto-Scaling Guide**](./docs/stress_testing_and_auto_scaling_guide.md) | Postman Performance Runner setup, Python load testing & ECS Auto-Scaling. | Markdown |
| 📦 [**ECS Task Definitions Explained**](./docs/ecs_task_definition_explained.md) | Student-friendly visual guide explaining Task Definitions vs Services. | Markdown |
| 🧹 [**AWS Teardown & Resource Cleanup**](./docs/aws_teardown_and_cleanup_guide.md) | Step-by-step instructions and 1-click script to delete all cloud resources ($0 bill). | Markdown |
| 📋 [**AWS Pre-Deployment Checklist**](./docs/aws_pre_deployment_checklist.md) | One-time AWS setup runbook for VPC, ALB, ACM, ECR, and Route 53. | Markdown |
| 🚀 [**AWS Fargate & CI/CD Deployment Guide**](./docs/aws_fargate_cicd_deployment_guide.md) | Deep-dive guide covering containerization, Nginx routing, and AWS security. | Markdown |
| 🌐 [**Nginx Routing & Reverse Proxy Explained**](./docs/nginx_explained.md) | Architectural breakdown of Nginx reverse proxying and caching headers. | Markdown |

---

## 📄 License & Attribution

Developed with ❤️ by **Sachin Mishra**.  
Architected for enterprise-scale autonomous AI retail applications.
