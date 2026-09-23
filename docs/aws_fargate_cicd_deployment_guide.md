# 🚀 AWS Fargate & GitHub Actions CI/CD Deployment Guide
### Production-Grade Containerized Deployment for Maison Luxé AI Stylist (STELLA)

---

## 📑 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [What is AWS Fargate & How It Works](#2-what-is-aws-fargate--how-it-works)
3. [Cloud Infrastructure Architecture](#3-cloud-infrastructure-architecture)
4. [Custom Domain Mapping: GoDaddy to AWS Route 53 & SSL (HTTPS)](#4-custom-domain-mapping-godaddy-to-aws-route-53--ssl-https)
5. [GitHub Actions CI/CD Pipeline Architecture](#5-github-actions-cicd-pipeline-architecture)
6. [Containerization & Docker Strategy](#6-containerization--docker-strategy)
7. [Security & Secrets Management](#7-security--secrets-management)
8. [Step-by-Step Deployment Runbook](#8-step-by-step-deployment-runbook)
9. [ECS Task Definitions](#9-ecs-task-definitions)
10. [GitHub Actions Workflow Configuration](#10-github-actions-workflow-configuration)
11. [Health Checks, Monitoring & Rollbacks](#11-health-checks-monitoring--rollbacks)
12. [Cost Optimization & Sizing Recommendations](#12-cost-optimization--sizing-recommendations)

---

## 1. Executive Summary

This architecture guide details the automated deployment of the **Maison Luxé Fashion Brand AI Agent (STELLA)** on **AWS ECS using AWS Fargate (Serverless Containers)**, automated via a **GitHub Actions CI/CD Pipeline**, and served securely under your custom domain: **`https://predictoraa.com`**.

### What Gets Deployed to AWS:
1. **Custom Domain & SSL**: **`https://predictoraa.com`** and **`https://www.predictoraa.com`** managed via **Amazon Route 53** (delegated from **GoDaddy**) with free, auto-renewing SSL/TLS certificates from **AWS Certificate Manager (ACM)**.
2. **Frontend**: Lightweight static web client (`index.html`, `style.css`, `app.js`) served by an enterprise-tuned **Nginx Alpine** container.
3. **Backend**: High-performance **FastAPI (Python 3.12)** application executing the STELLA LangChain agent, SenseNova LLM integration, and database orchestration.
4. **Application Load Balancer (ALB)**: A single internet-facing entrypoint terminating HTTPS (Port 443), redirecting HTTP (Port 80) $\rightarrow$ HTTPS, and routing traffic seamlessly between the frontend and backend microservices using path-based rules.

### What Stays in the Cloud (External):
- **MySQL Database**: Hosted on **Aiven Cloud** (port `16512`) storing product catalog, inventory, and customer loyalty records.
- **PostgreSQL Database**: Hosted on **Supabase** (port `5432` IPv4 connection pooler) storing multi-turn conversation checkpoints and agent memory.
- **SenseNova LLM API**: External AI inference provider.

---

## 2. What is AWS Fargate & How It Works

**AWS Fargate** is a serverless, pay-as-you-go compute engine that lets you run containers without managing virtual machines (EC2 instances).

### Traditional EC2 vs. AWS Fargate

| Dimension | Traditional EC2 ECS | AWS Fargate (Serverless) |
| :--- | :--- | :--- |
| **Server Management** | You provision, patch, monitor, and configure Linux EC2 instances. | **Zero server management**. AWS provisions and manages underlying hardware and OS. |
| **Capacity Planning** | Two levels of scaling: container task scaling + underlying EC2 scaling. | **One level of scaling**: scale tasks directly on demand. |
| **Security Isolation** | Multiple containers share the same Linux kernel on an EC2 host. | **Kernel-level MicroVM isolation** (via Firecracker). Each task runs in its own sandbox. |
| **Pricing Model** | Pay 24/7 for the EC2 instance uptime, regardless of container utilization. | Pay **strictly per-second** for the exact vCPU and Memory allocated to running tasks. |
| **Networking** | Shared host network or complex bridge overlays. | Every task gets a native **Elastic Network Interface (ENI)** with its own private IP address in your VPC. |

### Core Building Blocks in AWS ECS Fargate

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Amazon ECS Cluster                             │
│                                                                          │
│  ┌─────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │     Frontend Fargate Service    │  │    Backend Fargate Service     │ │
│  │                                 │  │                                │ │
│  │  ┌───────────────────────────┐  │  │  ┌───────────────────────────┐ │ │
│  │  │   Fargate Task (MicroVM)  │  │  │  │   Fargate Task (MicroVM)  │ │ │
│  │  │  ┌─────────────────────┐  │  │  │  │  ┌─────────────────────┐  │ │ │
│  │  │  │   Nginx Container   │  │  │  │  │  │  FastAPI Container  │  │ │ │
│  │  │  │   Port 80           │  │  │  │  │  │  Port 8000          │  │ │ │
│  │  │  └─────────────────────┘  │  │  │  │  └─────────────────────┘  │ │ │
│  │  │   0.25 vCPU · 512 MB RAM  │  │  │  │   0.5 vCPU · 1024 MB RAM  │ │ │
│  │  │   ENI: 10.0.1.42          │  │  │  │   ENI: 10.0.2.88          │ │ │
│  │  └───────────────────────────┘  │  │  └───────────────────────────┘ │ │
│  └─────────────────────────────────┘  └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

1. **ECS Cluster**: A logical grouping of services and tasks.
2. **Task Definition**: The declarative blueprint (JSON) specifying container images, resource limits (vCPU / Memory), environment variables, secrets, and CloudWatch log drivers.
3. **Task**: The active running instance of a Task Definition.
4. **Service**: The supervisor that maintains the desired number of healthy tasks, coordinates with the Load Balancer, and orchestrates zero-downtime rolling updates.

---

## 3. Cloud Infrastructure Architecture

Below is the production cloud deployment layout for Maison Luxé on AWS:

![AWS Fargate Infrastructure Architecture](./assets/fargate_architecture.jpg)

### Detailed Network & Traffic Flow

![Detailed Network & Traffic Flow](./assets/network_traffic_flowchart.jpg)

<details>
<summary><b>🔍 View Raw Mermaid Flowchart Code</b></summary>

```mermaid
flowchart TD
    subgraph Internet["Public Internet"]
        User["🌐 Shopper / Client Browser"]
    end

    subgraph AWS["AWS Cloud (VPC: 10.0.0.0/16)"]
        IGW["Internet Gateway (IGW)"]

        subgraph Public_Subnets["Public Subnets (AZ-1 & AZ-2)"]
            ALB["Application Load Balancer (ALB)\n(DNS: fashion-alb-xxxx.elb.amazonaws.com)\nPort 80 / 443"]
            
            subgraph TG_FE["Target Group: Frontend"]
                FE_Port["Forward to Port 80"]
            end

            subgraph TG_BE["Target Group: Backend"]
                BE_Port["Forward to Port 8000\nHealth: /health"]
            end
        end

        subgraph ECS_Cluster["Amazon ECS Cluster: fashion-agent-cluster"]
            subgraph FE_Service["Service: fashion-frontend-service"]
                FE_Task["Fargate Task (Nginx)\nServes: HTML, CSS, JS\nPort 80"]
            end

            subgraph BE_Service["Service: fashion-backend-service"]
                BE_Task["Fargate Task (FastAPI)\nRuns: STELLA LangChain Agent\nPort 8000"]
            end
        end

        subgraph AWS_Services["AWS Native Services"]
            ECR["Amazon ECR\n(Docker Image Registry)"]
            SSM["AWS Systems Manager\nParameter Store (Secrets)"]
            CW["CloudWatch Logs\n(/ecs/fashion-*)"]
        end
    end

    subgraph External_Databases["External Cloud Backends"]
        MySQL[("MySQL on Aiven Cloud\nHost: mysql-*.aivencloud.com\nPort: 16512")]
        Supabase[("PostgreSQL on Supabase\nHost: aws-0-ap-northeast-2.pooler.supabase.com\nPort: 5432")]
        SenseNova["SenseNova LLM API\n(Chat Completion Engine)"]
    end

    User -->|HTTP / HTTPS Request| IGW
    IGW --> ALB

    %% ALB Routing Rules
    ALB -->|"Rule 1: Path /chat*, /products*, /health*, /auth*"| TG_BE
    ALB -->|"Default Rule: Path /*"| TG_FE

    TG_FE --> FE_Task
    TG_BE --> BE_Task

    %% Outbound Database Connections
    BE_Task -->|MySQL Wire Protocol| MySQL
    BE_Task -->|PostgreSQL Wire Protocol| Supabase
    BE_Task -->|HTTPS API Requests| SenseNova

    %% Internal AWS Integrations
    BE_Task -.->|Fetch DB Passwords & Keys| SSM
    FE_Task & BE_Task -.->|Stream stdout/stderr| CW
    ECR -.->|Pull Image on Deploy| FE_Task & BE_Task
```
</details>

### Why a Single Application Load Balancer with Path Routing?

1. **Elimination of Cross-Origin Resource Sharing (CORS)**:
   - When the user visits `http://fashion-alb-xxxx.amazonaws.com/`, the frontend loads.
   - When `app.js` calls `fetch("/chat")`, the request goes to the **exact same host**.
   - The ALB automatically forwards `/chat` to the backend container.
   - Result: No browser CORS errors, no preflight `OPTIONS` overhead.
2. **Cost Optimization**:
   - An AWS ALB costs ~$16–$22/month base price. Running 2 separate ALBs for frontend and backend doubles this cost. A single ALB with listener routing rules saves ~50%.
3. **Decoupled Deployments**:
   - Frontend and backend live in separate ECS Services. If you push a UI change, only the frontend container restarts. The backend agent remains running without interruption.

---

## 4. Custom Domain Mapping: GoDaddy to AWS Route 53 & SSL (HTTPS)

You can launch and host the Maison Luxé UI and API directly under your custom domain **`https://predictoraa.com`** (and **`https://www.predictoraa.com`**).

AWS provides two services specifically designed for this:
1. **Amazon Route 53**: AWS's highly scalable and available cloud Domain Name System (DNS) web service (named after TCP/UDP Port 53). It manages your DNS records and supports native **ALIAS records** that map your root domain (`predictoraa.com`) directly to your AWS Application Load Balancer with zero performance latency.
2. **AWS Certificate Manager (ACM)**: Issues **free, automatically-renewing SSL/TLS certificates** so your website has a trusted HTTPS padlock in every browser.

Below is the complete architectural layout of how traffic flows from GoDaddy through Route 53 to your Fargate containers:

![GoDaddy to Route 53 Domain Mapping](./assets/route53_domain_mapping.jpg)

---

### Step-by-Step Domain Mapping Workflow



#### Step 1: Create a Public Hosted Zone in AWS Route 53
In the AWS Management Console or AWS CLI, create a Public Hosted Zone for `predictoraa.com`.
Route 53 will automatically assign a set of **4 authoritative nameservers** (NS records), for example:
- `ns-1234.awsdns-12.org`
- `ns-567.awsdns-34.com`
- `ns-890.awsdns-56.net`
- `ns-123.awsdns-78.co.uk`

#### Step 2: Delegate Nameservers in GoDaddy
Log into your **GoDaddy Account**:
1. Go to **My Products** $\rightarrow$ **Domains** $\rightarrow$ Click **predictoraa.com**.
2. Select **DNS** (or **Manage DNS**) $\rightarrow$ Navigate to the **Nameservers** section.
3. Click **Change Nameservers** (or **Enter my own nameservers (advanced)**).
4. Replace GoDaddy's default nameservers with the **4 AWS Route 53 nameserver addresses** from Step 1.
5. Save changes. *(DNS delegation typically propagates across the global internet in 5 to 30 minutes).*

> [!NOTE]
> **Why delegate nameservers to Route 53 instead of keeping GoDaddy DNS?**
> Standard DNS providers like GoDaddy do not support CNAME records on the root/apex domain (`predictoraa.com` without `www`). AWS ALBs use dynamic IP addresses and provide a DNS name rather than a static IP. Route 53 provides a proprietary **A (Alias)** record type that allows mapping root domains directly to an ALB at the DNS resolution level with zero redirect hops.

#### Step 3: Request a Free SSL/TLS Certificate via AWS Certificate Manager (ACM)
1. In the AWS Console, navigate to **AWS Certificate Manager (ACM)** in the same region as your ALB.
2. Click **Request a certificate** $\rightarrow$ **Request a public certificate**.
3. In **Domain names**, enter:
   - `predictoraa.com`
   - `*.predictoraa.com` (covers `www.predictoraa.com` and all subdomains).
4. Select **DNS validation**.
5. Once requested, click **Create records in Route 53**. Route 53 will automatically write the required CNAME verification records into your hosted zone.
6. The certificate status will switch to **Issued** within 2–5 minutes.

#### Step 4: Configure ALB HTTPS Listener (Port 443) & HTTP Redirect (Port 80)
1. **HTTPS Listener (Port 443)**:
   - Add a listener for HTTPS on Port 443.
   - Attach the ACM certificate for `predictoraa.com`.
   - Default action: Forward to `tg-fashion-frontend` (Port 80).
   - Add path-based routing rule: Forward `/chat*`, `/products*`, `/health*`, `/auth*` to `tg-fashion-backend` (Port 8000).
2. **HTTP Listener (Port 80) - Automatic Redirect**:
   - Update the existing Port 80 listener to **Redirect to HTTPS Port 443** (HTTP 301 Permanent Redirect) to enforce encryption for all visitors.

#### Step 5: Create Route 53 A-Alias Records for the Domain
In your Route 53 Hosted Zone for `predictoraa.com`:
1. Click **Create Record**:
   - **Record name**: *(leave blank for apex `predictoraa.com`)*
   - **Record type**: `A`
   - **Alias**: Toggle **ON**
   - **Route traffic to**: Alias to Application and Classic Load Balancer
   - **Region**: Choose your ALB's AWS Region
   - **Load Balancer**: Select your `alb-fashion-agent`
2. Create a second record for `www`:
   - **Record name**: `www`
   - **Record type**: `A`
   - **Alias**: Toggle **ON**
   - **Route traffic to**: Alias to Application and Classic Load Balancer
   - **Load Balancer**: Select your `alb-fashion-agent`

Now, visiting `http://predictoraa.com`, `http://www.predictoraa.com`, or `https://predictoraa.com` will automatically lead to your Maison Luxé AI Stylist securely over SSL/TLS!

---

## 5. GitHub Actions CI/CD Pipeline Architecture

Below is the automated continuous integration and delivery lifecycle with distinct **CI (Testing & Linting)** and **CD (Cloud Docker Build & Deployment)** phases:

![GitHub Actions CI/CD Pipeline](./assets/cicd_pipeline.jpg)

### Pipeline Flow Diagram

![CI/CD Pipeline Flow Diagram](./assets/cicd_pipeline_flowchart.jpg)

<details>
<summary><b>🔍 View Raw Mermaid Sequence Diagram Code</b></summary>

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant GH as GitHub Actions Runner (Cloud)
    participant OIDC as AWS IAM (OIDC Role)
    participant ECR as Amazon ECR
    participant ECS as AWS ECS (Fargate)
    participant ALB as Application Load Balancer

    Dev->>GH: git push origin main
    
    rect rgb(28, 40, 58)
        note over GH: PHASE 1: CONTINUOUS INTEGRATION (CI QUALITY GATE)
        GH->>GH: Checkout Code
        GH->>GH: Set up Python 3.12 & install dependencies
        GH->>GH: 1. Code Linting (Ruff / Flake8)
        GH->>GH: 2. Code Formatting Verification (Black)
        GH->>GH: 3. Run Pytest Unit & Integration Tests
        GH->>GH: 4. Static Code & Security Analysis
        alt CI Tests or Lint Fails ❌
            GH-->>Dev: Pipeline Fails Immediately! (No Docker build)
        end
    end

    rect rgb(20, 45, 35)
        note over GH: PHASE 2: CONTINUOUS DELIVERY & DEPLOYMENT (CD - IN CLOUD)
        note over GH: Docker image is built on GitHub Actions Cloud Runner, NOT locally!
        GH->>OIDC: Authenticate via OpenID Connect (OIDC)
        OIDC-->>GH: Issue temporary AWS STS credentials
        GH->>GH: Build Docker Image in GitHub Cloud Runner (python:3.12-slim)
        GH->>GH: Run Container Security Scan (CVE checks)
        GH->>ECR: Push image with tags :${{ github.sha }} and :latest
        GH->>GH: Render ecs-backend-task.json with new SHA tag
        GH->>ECS: Register new Task Definition & Update Service
        note over ECS: Zero-Downtime Rolling Update on Fargate
        ECS->>ECS: Launch new Task in dedicated MicroVM
        ECS->>ALB: Register new Task & wait for /health 200 OK
        ALB->>ECS: Target Healthy! Shift live traffic to new Task
        ECS->>ECS: Gracefully drain & terminate old Task
    end

    GH-->>Dev: Pipeline Success Notification ✅ (Live on predictoraa.com)
```
</details>

### Key Highlights of the CI/CD Pipeline

1. **Strict Quality Gate (CI Phase Before Any Image Build)**:
   - Every commit triggers automated linting (`ruff` / `flake8`), code formatting checks (`black --check`), and unit tests (`pytest`).
   - If a test or linting error occurs, the pipeline fails immediately. **No Docker image is ever built or pushed to AWS.**
2. **Cloud-Native Image Building (Never Built Locally for Deployment)**:
   - The production Docker image is built entirely within the secure, ephemeral **GitHub Actions cloud runner (`ubuntu-latest`)** using Docker BuildKit.
   - Developers only build Docker images locally for sandbox debugging; all production images originate immutably in the cloud.
3. **Zero Hardcoded AWS Credentials (OIDC)**:
   - Uses **GitHub OpenID Connect (OIDC)** to securely assume an IAM role. No permanent `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` needs to be saved in GitHub.
4. **Smart Path Filtering**:
   - Editing frontend files triggers only the frontend CI/CD pipeline (~45s). Updating backend Python files triggers the backend CI/CD pipeline.
5. **Zero-Downtime Rolling Rollouts**:
   - ECS Fargate launches the new container, waits for the ALB health check (`GET /health` $\rightarrow$ 200 OK) to pass, smoothly shifts live production traffic to it, and drains the old container without dropping a single active customer request.

---

## 6. Containerization & Docker Strategy

### 5.1 Backend Containerization

**Location**: `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies needed for compiling psycopg and network checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

EXPOSE 8000

# Container healthcheck querying FastAPI /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production server execution with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Location**: `backend/.dockerignore`
```
__pycache__
*.pyc
*.pyo
*.pyd
.venv
.env
.git
.gitignore
.DS_Store
tests
.pytest_cache
```

---

### 5.2 Frontend Containerization

**Location**: `frontend/Dockerfile`
```dockerfile
FROM nginx:1.27-alpine

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static frontend assets
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**Location**: `frontend/nginx.conf`
```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip Compression for high-performance delivery
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/json;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Cache static assets
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800, immutable";
    }

    # SPA routing fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 5.3 Dynamic Frontend API Base URL

In `frontend/app.js`, configure the API target dynamically so the frontend seamlessly talks to `http://localhost:8000` during local development, and automatically uses the same-origin ALB path in production on AWS:

```javascript
// Automatically detects environment
const API_BASE = (window.location.hostname === "localhost" && window.location.port === "3000")
  ? "http://localhost:8000"  // Local dev server
  : "";                      // Production AWS ALB (same origin)
```

---

## 7. Security & Secrets Management

Your database and API secrets **must never be baked into Docker images** or committed to GitHub.

### AWS Systems Manager (SSM) Parameter Store Setup

Store your secrets as `SecureString` in AWS SSM Parameter Store:

```bash
# SenseNova API Key
aws ssm put-parameter \
  --name "/fashion-agent/SENSENOVA_API_KEY" \
  --value "YOUR_SENSENOVA_API_KEY" \
  --type "SecureString"

# MySQL Credentials (Aiven Cloud)
aws ssm put-parameter --name "/fashion-agent/MYSQL_HOST" --value "YOUR_AIVEN_MYSQL_HOST" --type "String"
aws ssm put-parameter --name "/fashion-agent/MYSQL_PORT" --value "16512" --type "String"
aws ssm put-parameter --name "/fashion-agent/MYSQL_USER" --value "avnadmin" --type "String"
aws ssm put-parameter --name "/fashion-agent/MYSQL_PASSWORD" --value "YOUR_AIVEN_MYSQL_PASSWORD" --type "SecureString"
aws ssm put-parameter --name "/fashion-agent/MYSQL_DATABASE" --value "defaultdb" --type "String"

# Supabase PostgreSQL Pooler Credentials
aws ssm put-parameter --name "/fashion-agent/POSTGRES_HOST" --value "YOUR_SUPABASE_POOLER_HOST" --type "String"
aws ssm put-parameter --name "/fashion-agent/POSTGRES_PORT" --value "5432" --type "String"
aws ssm put-parameter --name "/fashion-agent/POSTGRES_USER" --value "postgres.YOUR_PROJECT_REF" --type "String"
aws ssm put-parameter --name "/fashion-agent/POSTGRES_PASSWORD" --value "YOUR_SUPABASE_PASSWORD" --type "SecureString"
aws ssm put-parameter --name "/fashion-agent/POSTGRES_DB" --value "postgres" --type "String"
aws ssm put-parameter --name "/fashion-agent/POSTGRES_CONN_STR" --value "postgresql://postgres.YOUR_PROJECT_REF:YOUR_SUPABASE_PASSWORD@YOUR_SUPABASE_POOLER_HOST:5432/postgres" --type "SecureString"
```

AWS Fargate automatically resolves these secrets at startup and exposes them to FastAPI as standard environment variables via the `secrets` stanza in the Task Definition.

---

## 8. Step-by-Step Deployment Runbook

### Step 1: Initial AWS Prerequisites Setup

Create the IAM Execution Role that allows Fargate tasks to read SSM secrets and write CloudWatch logs:

```bash
# 1. Create IAM execution role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": { "Service": "ecs-tasks.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }]
  }'

# 2. Attach basic ECS execution policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# 3. Attach inline policy to read SSM Parameters
aws iam put-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-name ReadSSMParameters \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters",
        "secretsmanager:GetSecretValue",
        "kms:Decrypt"
      ],
      "Resource": "*"
    }]
  }'
```

### Step 2: Create Amazon ECR Repositories

```bash
# Create Backend ECR Repository
aws ecr create-repository \
  --repository-name fashion-backend \
  --image-scanning-configuration scanOnPush=true

# Create Frontend ECR Repository
aws ecr create-repository \
  --repository-name fashion-frontend \
  --image-scanning-configuration scanOnPush=true
```

### Step 3: Create CloudWatch Log Groups

```bash
aws logs create-log-group --log-group-name /ecs/fashion-backend
aws logs create-log-group --log-group-name /ecs/fashion-frontend
```

### Step 4: Create Application Load Balancer & Target Groups

```bash
# 1. Create Target Group for Frontend (Port 80)
aws elbv2 create-target-group \
  --name tg-fashion-frontend \
  --protocol HTTP \
  --port 80 \
  --target-type ip \
  --vpc-id <YOUR_VPC_ID> \
  --health-check-path /

# 2. Create Target Group for Backend (Port 8000)
aws elbv2 create-target-group \
  --name tg-fashion-backend \
  --protocol HTTP \
  --port 8000 \
  --target-type ip \
  --vpc-id <YOUR_VPC_ID> \
  --health-check-path /health \
  --health-check-interval-seconds 30

# 3. Create ALB
aws elbv2 create-load-balancer \
  --name alb-fashion-agent \
  --subnets <PUBLIC_SUBNET_1> <PUBLIC_SUBNET_2> \
  --security-groups <ALB_SECURITY_GROUP_ID>

# 4. Create Listener (Port 80) that automatically redirects all HTTP traffic to HTTPS (Port 443)
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'

# 5. Create HTTPS Listener (Port 443) terminating SSL with ACM certificate
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<ACM_CERTIFICATE_ARN> \
  --default-actions Type=forward,TargetGroupArn=<FRONTEND_TG_ARN>

# 6. Add Path Rule for Backend API traffic on the HTTPS listener
aws elbv2 create-rule \
  --listener-arn <HTTPS_LISTENER_ARN> \
  --priority 10 \
  --conditions Field=path-pattern,Values='/chat*','/products*','/health*','/auth*' \
  --actions Type=forward,TargetGroupArn=<BACKEND_TG_ARN>
```

### Step 5: Configure Route 53 Domain Mapping for `predictoraa.com`

```bash
# 1. Create Route 53 Hosted Zone
aws route53 create-hosted-zone \
  --name predictoraa.com \
  --caller-reference "predictoraa-$(date +%s)"

# (Note the 4 Nameservers outputted, e.g. ns-xxx.awsdns-xx.com, and enter them in GoDaddy)

# 2. Request Free Public SSL Certificate via ACM
aws acm request-certificate \
  --domain-name predictoraa.com \
  --subject-alternative-names "*.predictoraa.com" \
  --validation-method DNS \
  --region <YOUR_AWS_REGION>

# 3. In Route 53, create A (Alias) records mapping predictoraa.com and www to your ALB:
aws route53 change-resource-record-sets \
  --hosted-zone-id <YOUR_HOSTED_ZONE_ID> \
  --change-batch '{
    "Changes": [
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "predictoraa.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "<ALB_CANONICAL_HOSTED_ZONE_ID>",
            "DNSName": "<ALB_DNS_NAME>",
            "EvaluateTargetHealth": true
          }
        }
      },
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "www.predictoraa.com",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "<ALB_CANONICAL_HOSTED_ZONE_ID>",
            "DNSName": "<ALB_DNS_NAME>",
            "EvaluateTargetHealth": true
          }
        }
      }
    ]
  }'
```

### Step 6: Create ECS Cluster & Initial Services

```bash
# 1. Create the Cluster
aws ecs create-cluster --cluster-name fashion-agent-cluster

# 2. Create Backend Service
aws ecs create-service \
  --cluster fashion-agent-cluster \
  --service-name fashion-backend-service \
  --task-definition fashion-backend \
  --launch-type FARGATE \
  --desired-count 1 \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_1>,<SUBNET_2>],securityGroups=[<BE_SG_ID>],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=<BACKEND_TG_ARN>,containerName=fashion-backend,containerPort=8000

# 3. Create Frontend Service
aws ecs create-service \
  --cluster fashion-agent-cluster \
  --service-name fashion-frontend-service \
  --task-definition fashion-frontend \
  --launch-type FARGATE \
  --desired-count 1 \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_1>,<SUBNET_2>],securityGroups=[<FE_SG_ID>],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=<FRONTEND_TG_ARN>,containerName=fashion-frontend,containerPort=80
```

---

## 9. ECS Task Definitions

### 8.1 Backend Task Definition Template
**File**: `deploy/ecs-backend-task.json`

```json
{
  "family": "fashion-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "fashion-backend",
      "image": "<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/fashion-backend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "secrets": [
        { "name": "SENSENOVA_API_KEY", "valueFrom": "/fashion-agent/SENSENOVA_API_KEY" },
        { "name": "MYSQL_HOST", "valueFrom": "/fashion-agent/MYSQL_HOST" },
        { "name": "MYSQL_PORT", "valueFrom": "/fashion-agent/MYSQL_PORT" },
        { "name": "MYSQL_USER", "valueFrom": "/fashion-agent/MYSQL_USER" },
        { "name": "MYSQL_PASSWORD", "valueFrom": "/fashion-agent/MYSQL_PASSWORD" },
        { "name": "MYSQL_DATABASE", "valueFrom": "/fashion-agent/MYSQL_DATABASE" },
        { "name": "POSTGRES_HOST", "valueFrom": "/fashion-agent/POSTGRES_HOST" },
        { "name": "POSTGRES_PORT", "valueFrom": "/fashion-agent/POSTGRES_PORT" },
        { "name": "POSTGRES_USER", "valueFrom": "/fashion-agent/POSTGRES_USER" },
        { "name": "POSTGRES_PASSWORD", "valueFrom": "/fashion-agent/POSTGRES_PASSWORD" },
        { "name": "POSTGRES_DB", "valueFrom": "/fashion-agent/POSTGRES_DB" },
        { "name": "POSTGRES_CONN_STR", "valueFrom": "/fashion-agent/POSTGRES_CONN_STR" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fashion-backend",
          "awslogs-region": "<REGION>",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

### 8.2 Frontend Task Definition Template
**File**: `deploy/ecs-frontend-task.json`

```json
{
  "family": "fashion-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "fashion-frontend",
      "image": "<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/fashion-frontend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fashion-frontend",
          "awslogs-region": "<REGION>",
          "awslogs-stream-prefix": "frontend"
        }
      }
    }
  ]
}
```

---

## 10. GitHub Actions Workflow Configuration

**File**: `.github/workflows/deploy.yml`

This complete workflow handles authentication via OIDC or Secrets, builds only the affected services, pushes them to ECR, and triggers rolling zero-downtime updates on ECS.

name: CI/CD Pipeline - AWS ECS Fargate

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: ${{ secrets.AWS_REGION || 'ap-south-1' }}
  ECR_BACKEND_REPO: fashion-backend
  ECR_FRONTEND_REPO: fashion-frontend
  ECS_CLUSTER: fashion-agent-cluster
  ECS_BACKEND_SERVICE: fashion-backend-service
  ECS_FRONTEND_SERVICE: fashion-frontend-service

permissions:
  id-token: write   # Required for AWS OIDC authentication
  contents: read

jobs:
  # ═════════════════════════════════════════════════════════════
  # STAGE 1: CONTINUOUS INTEGRATION (CI) - BACKEND QUALITY GATE
  # ═════════════════════════════════════════════════════════════
  ci-backend:
    name: "CI: Lint & Test Backend"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Check for Backend Changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters:
            backend:
              - 'backend/**'
              - '.github/workflows/deploy.yml'

      - name: Set up Python 3.12
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install Dependencies & Test Tools
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        run: |
          python -m pip install --upgrade pip
          pip install ruff black pytest httpx
          pip install -r backend/requirements.txt

      - name: 1. Code Linting (Ruff)
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        run: |
          echo "Running code linter on backend/..."
          ruff check backend/ --ignore E501

      - name: 2. Code Formatting Verification (Black)
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        run: |
          echo "Verifying code formatting..."
          black --check backend/

      - name: 3. Run Automated Tests (Pytest)
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        run: |
          echo "Executing test suite..."
          pytest backend/tests/ -v

  # ═════════════════════════════════════════════════════════════
  # STAGE 1: CONTINUOUS INTEGRATION (CI) - FRONTEND QUALITY GATE
  # ═════════════════════════════════════════════════════════════
  ci-frontend:
    name: "CI: Validate Frontend"
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Check for Frontend Changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters:
            frontend:
              - 'frontend/**'
              - '.github/workflows/deploy.yml'

      - name: Validate Frontend Assets
        if: steps.filter.outputs.frontend == 'true' || github.event_name == 'workflow_dispatch'
        run: |
          echo "Verifying frontend HTML, CSS, and JS file presence and syntax..."
          test -f frontend/index.html || exit 1
          test -f frontend/style.css || exit 1
          test -f frontend/app.js || exit 1
          node -c frontend/app.js
          echo "Frontend syntax validation passed!"

  # ═════════════════════════════════════════════════════════════
  # STAGE 2: CONTINUOUS DEPLOYMENT (CD) - CLOUD BUILD & ECS BACKEND
  # (Only runs if CI passes & code is merged to main)
  # ═════════════════════════════════════════════════════════════
  deploy-backend:
    name: "CD: Cloud Build & Deploy Backend"
    needs: [ci-backend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Check for Backend Changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters:
            backend:
              - 'backend/**'
              - 'deploy/ecs-backend-task.json'
              - '.github/workflows/deploy.yml'

      - name: Configure AWS Credentials (OIDC or Secret Keys)
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Log in to Amazon ECR
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx (Cloud Builder)
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        uses: docker/setup-buildx-action@v3

      - name: Build, Tag, and Push Backend Image in GitHub Actions Cloud
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          echo "Building Docker container image inside GitHub Actions cloud runner (NOT locally)..."
          docker build \
            --cache-from=type=gha \
            --cache-to=type=gha,mode=max \
            -t $ECR_REGISTRY/$ECR_BACKEND_REPO:$IMAGE_TAG \
            -t $ECR_REGISTRY/$ECR_BACKEND_REPO:latest \
            ./backend

          echo "Pushing image to Amazon ECR..."
          docker push $ECR_REGISTRY/$ECR_BACKEND_REPO:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_BACKEND_REPO:latest
          echo "image=$ECR_REGISTRY/$ECR_BACKEND_REPO:$IMAGE_TAG" >> $GITHUB_OUTPUT
        id: build-image

      - name: Render Backend Task Definition
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        id: render-task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: deploy/ecs-backend-task.json
          container-name: fashion-backend
          image: ${{ steps.build-image.outputs.image }}

      - name: Deploy Backend to Amazon ECS (Zero-Downtime Rolling Update)
        if: steps.filter.outputs.backend == 'true' || github.event_name == 'workflow_dispatch'
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.render-task-def.outputs.task-definition }}
          service: ${{ env.ECS_BACKEND_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true

  # ═════════════════════════════════════════════════════════════
  # STAGE 2: CONTINUOUS DEPLOYMENT (CD) - CLOUD BUILD & ECS FRONTEND
  # (Only runs if CI passes & code is merged to main)
  # ═════════════════════════════════════════════════════════════
  deploy-frontend:
    name: "CD: Cloud Build & Deploy Frontend"
    needs: [ci-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Check for Frontend Changes
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters:
            frontend:
              - 'frontend/**'
              - 'deploy/ecs-frontend-task.json'
              - '.github/workflows/deploy.yml'

      - name: Configure AWS Credentials
        if: steps.filter.outputs.frontend == 'true' || github.event_name == 'workflow_dispatch'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Log in to Amazon ECR
        if: steps.filter.outputs.frontend == 'true' || github.event_name == 'workflow_dispatch'
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, Tag, and Push Frontend Image in GitHub Actions Cloud
        if: steps.filter.outputs.frontend == 'true' || github.event_name == 'workflow_dispatch'
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          echo "Building Frontend Nginx image in GitHub Actions cloud runner..."
          docker build \
            -t $ECR_REGISTRY/$ECR_FRONTEND_REPO:$IMAGE_TAG \
            -t $ECR_REGISTRY/$ECR_FRONTEND_REPO:latest \
            ./frontend

          echo "Pushing image to Amazon ECR..."
          docker push $ECR_REGISTRY/$ECR_FRONTEND_REPO:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_FRONTEND_REPO:latest
          echo "image=$ECR_REGISTRY/$ECR_FRONTEND_REPO:$IMAGE_TAG" >> $GITHUB_OUTPUT
        id: build-image

      - name: Render Frontend Task Definition
        if: steps.filter.outputs.frontend == 'true' || github.event_name == 'workflow_dispatch'
        id: render-task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: deploy/ecs-frontend-task.json
          container-name: fashion-frontend
          image: ${{ steps.build-image.outputs.image }}

      - name: Deploy Frontend to Amazon ECS (Zero-Downtime Rolling Update)
        if: steps.filter.outputs.frontend == 'true' || github.event_name == 'workflow_dispatch'
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.render-task-def.outputs.task-definition }}
          service: ${{ env.ECS_FRONTEND_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
```

---

## 11. Health Checks, Monitoring & Rollbacks

### Live Container Log Inspection
Tail live streaming logs from running Fargate tasks using the AWS CLI:
```bash
# Follow backend logs
aws logs tail /ecs/fashion-backend --follow

# Follow frontend access logs
aws logs tail /ecs/fashion-frontend --follow
```

### Zero-Downtime Rollback Strategy
If a deployment exhibits unexpected behavior in production, rolling back takes seconds:
1. **Instant Task Rollback via CLI**:
   ```bash
   # Re-point the service to the previous Task Definition revision (e.g., revision 3)
   aws ecs update-service \
     --cluster fashion-agent-cluster \
     --service fashion-backend-service \
     --task-definition fashion-backend:3
   ```
2. **Git-Based Rollback**:
   Revert the commit on `main` (`git revert HEAD && git push origin main`). GitHub Actions will automatically rebuild the verified previous code and update the service.

---

## 12. Cost Optimization & Sizing Recommendations

For standard production workloads running 24/7 on AWS Fargate in regions like `ap-south-1` or `us-east-1`:

| Service / Resource | Sizing | Estimated Monthly Cost |
| :--- | :--- | :--- |
| **Backend Fargate Task** | 0.5 vCPU · 1024 MB RAM (1 Task) | ~$14.50 / month |
| **Frontend Fargate Task** | 0.25 vCPU · 512 MB RAM (1 Task) | ~$7.25 / month |
| **Application Load Balancer (ALB)** | 1 ALB (shared by both services) | ~$18.00 / month |
| **Amazon Route 53 (DNS)** | 1 Hosted Zone (`predictoraa.com`) | ~$0.50 / month |
| **AWS Certificate Manager (ACM)** | Wildcard SSL/TLS Certificate | **$0.00** (Free with AWS ALB) |
| **Amazon ECR & CloudWatch Logs** | Image storage (~5 GB) + Logs | ~$1.50 / month |
| **External Databases (Aiven & Supabase)** | Already running externally | $0.00 additional |
| **Total Estimated Cost** | | **~$41.75 / month** |

> [!TIP]
> **Fargate Spot**: You can reduce the compute costs by up to **70%** by configuring your ECS Service to use `FARGATE_SPOT` capacity provider for non-critical environments.
