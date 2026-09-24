#!/usr/bin/env python3
"""
scripts/generate_architecture_diagram.py
Generates a publication-grade, official AWS-style Architecture Diagram for Maison Luxé (STELLA).
Outputs high-resolution SVG, PNG, and JPG files into the docs/ directory.
"""
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

def generate_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1250" width="2000" height="1250" style="background:#F8F9FA; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Gradients & Drop Shadows -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0F172A" flood-opacity="0.08"/>
    </filter>
    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#FF9900" flood-opacity="0.3"/>
    </filter>
    
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    
    <linearGradient id="awsCardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#F8FAFC"/>
    </linearGradient>

    <!-- Arrow Markers -->
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284C7"/>
    </marker>
    <marker id="arrow-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#EA580C"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16A34A"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#9333EA"/>
    </marker>
    <marker id="arrow-gray" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748B"/>
    </marker>
  </defs>

  <!-- ==================== TOP HEADER BANNER ==================== -->
  <rect x="0" y="0" width="2000" height="90" fill="url(#headerGrad)"/>
  <rect x="0" y="86" width="2000" height="4" fill="#FF9900"/>
  
  <!-- AWS Logo Badge -->
  <rect x="35" y="18" width="54" height="54" rx="8" fill="#FF9900"/>
  <text x="62" y="52" fill="#0F172A" font-size="20" font-weight="900" text-anchor="middle">AWS</text>
  
  <text x="110" y="44" fill="#FFFFFF" font-size="24" font-weight="800" letter-spacing="-0.5">Maison Luxé (STELLA) — Production AWS Cloud Architecture</text>
  <text x="110" y="68" fill="#94A3B8" font-size="14" font-weight="500">Autonomous Fashion Brand Agent | ECS Fargate Serverless | GitHub Actions CI/CD | https://predictoraa.com</text>

  <!-- Region / Status Tags -->
  <rect x="1750" y="26" width="210" height="38" rx="6" fill="#1E293B" stroke="#334155" stroke-width="1"/>
  <circle cx="1772" cy="45" r="6" fill="#22C55E"/>
  <text x="1786" y="50" fill="#E2E8F0" font-size="13" font-weight="600">Region: ap-south-1</text>

  <!-- ==================== LEFT COLUMN: USERS, GODADDY, ROUTE 53 ==================== -->
  
  <!-- 1. Client Shopper -->
  <g transform="translate(40, 130)">
    <rect width="180" height="120" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" filter="url(#shadow)"/>
    <rect x="15" y="15" width="40" height="40" rx="20" fill="#E0F2FE"/>
    <text x="35" y="41" font-size="20" text-anchor="middle">🌐</text>
    <text x="65" y="34" fill="#0F172A" font-size="15" font-weight="700">Client / Shopper</text>
    <text x="65" y="52" fill="#64748B" font-size="12">Web Browser</text>
    <rect x="15" y="70" width="150" height="32" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>
    <text x="90" y="91" fill="#0284C7" font-size="11" font-weight="600" text-anchor="middle">predictoraa.com</text>
  </g>

  <!-- 2. GoDaddy Registrar -->
  <g transform="translate(40, 300)">
    <rect width="180" height="135" rx="10" fill="#FFFFFF" stroke="#00A4A6" stroke-width="2" filter="url(#shadow)"/>
    <rect x="15" y="15" width="40" height="40" rx="8" fill="#CCFBF1"/>
    <text x="35" y="42" font-size="20" text-anchor="middle">🏢</text>
    <text x="65" y="34" fill="#0F172A" font-size="15" font-weight="700">GoDaddy DNS</text>
    <text x="65" y="52" fill="#0D9488" font-size="11" font-weight="600">Domain Registrar</text>
    <rect x="15" y="70" width="150" height="48" rx="6" fill="#F0FDFA" stroke="#99F6E4" stroke-width="1"/>
    <text x="90" y="88" fill="#0F766E" font-size="10" font-weight="600" text-anchor="middle">Delegates 4 NS to</text>
    <text x="90" y="104" fill="#0F766E" font-size="10" font-weight="700" text-anchor="middle">AWS Route 53</text>
  </g>

  <!-- 3. Amazon Route 53 & ACM Container -->
  <g transform="translate(40, 480)">
    <rect width="180" height="250" rx="10" fill="#FFFFFF" stroke="#8C4FFF" stroke-width="2" filter="url(#shadow)"/>
    
    <!-- Route 53 Header -->
    <rect x="15" y="15" width="36" height="36" rx="8" fill="#F3E8FF"/>
    <text x="33" y="40" font-size="18" text-anchor="middle">🗺️</text>
    <text x="58" y="32" fill="#0F172A" font-size="14" font-weight="700">Route 53</text>
    <text x="58" y="48" fill="#7E22CE" font-size="11" font-weight="600">Hosted Zone</text>
    
    <!-- Records Box -->
    <rect x="12" y="65" width="156" height="85" rx="6" fill="#FAF5FF" stroke="#E9D5FF" stroke-width="1"/>
    <text x="20" y="83" fill="#6B21A8" font-size="10" font-weight="700">A (Alias) ➔ ALB</text>
    <text x="20" y="98" fill="#475569" font-size="9.5">predictoraa.com</text>
    <text x="20" y="113" fill="#475569" font-size="9.5">www.predictoraa.com</text>
    <text x="20" y="132" fill="#6B21A8" font-size="9.5" font-weight="600">DNS Validation CNAME</text>

    <!-- ACM Certificate Box -->
    <rect x="12" y="160" width="156" height="75" rx="6" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1"/>
    <text x="20" y="180" fill="#15803D" font-size="11" font-weight="700">🔒 AWS ACM</text>
    <text x="20" y="198" fill="#166534" font-size="10" font-weight="600">SSL/TLS Certificate</text>
    <text x="20" y="214" fill="#334155" font-size="9.5">*.predictoraa.com</text>
    <text x="20" y="228" fill="#15803D" font-size="9" font-weight="700">Status: Issued ✅</text>
  </g>

  <!-- ==================== MAIN AWS CLOUD (VPC) CONTAINER ==================== -->
  <g transform="translate(260, 115)">
    <!-- AWS Cloud Outer Boundary -->
    <rect width="1240" height="760" rx="14" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="8 6"/>
    
    <!-- Cloud Header Badge -->
    <rect x="20" y="-14" width="220" height="28" rx="6" fill="#232F3E"/>
    <text x="130" y="5" fill="#FF9900" font-size="12" font-weight="700" text-anchor="middle">☁️ AWS Cloud (ap-south-1)</text>

    <!-- Default VPC Container -->
    <g transform="translate(25, 30)">
      <rect width="1190" height="705" rx="12" fill="#F8FAFC" stroke="#0073BB" stroke-width="2.5"/>
      <rect x="20" y="-12" width="200" height="24" rx="4" fill="#0073BB"/>
      <text x="120" y="4" fill="#FFFFFF" font-size="11" font-weight="700" text-anchor="middle">VPC: 172.31.0.0/16 (Default)</text>

      <!-- Internet Gateway -->
      <g transform="translate(40, 25)">
        <rect width="140" height="45" rx="6" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.5"/>
        <text x="70" y="28" fill="#0369A1" font-size="12" font-weight="700" text-anchor="middle">🌐 Internet Gateway</text>
      </g>

      <!-- Application Load Balancer Section -->
      <g transform="translate(40, 95)">
        <rect width="1110" height="155" rx="10" fill="#FFFFFF" stroke="#8C4FFF" stroke-width="2" filter="url(#shadow)"/>
        
        <!-- ALB Header -->
        <rect x="20" y="15" width="40" height="40" rx="8" fill="#F3E8FF"/>
        <text x="40" y="41" font-size="20" text-anchor="middle">⚖️</text>
        <text x="70" y="32" fill="#0F172A" font-size="16" font-weight="800">Application Load Balancer (ALB: alb-fashion-agent)</text>
        <text x="70" y="50" fill="#64748B" font-size="12">Security Group: <tspan fill="#DC2626" font-weight="600">alb-sg</tspan> (Inbound Ports 80 &amp; 443 from 0.0.0.0/0) | DualStack Internet-Facing</text>

        <!-- Listener 80 Box -->
        <g transform="translate(30, 75)">
          <rect width="280" height="60" rx="6" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1"/>
          <text x="15" y="24" fill="#1E40AF" font-size="12" font-weight="700">HTTP Listener (Port 80)</text>
          <text x="15" y="44" fill="#1D4ED8" font-size="11">Default: HTTP 301 Permanent Redirect ➔ HTTPS:443</text>
        </g>

        <!-- Listener 443 Box -->
        <g transform="translate(330, 75)">
          <rect width="750" height="60" rx="6" fill="#FDF4FF" stroke="#F0ABFC" stroke-width="1"/>
          <text x="15" y="24" fill="#86198F" font-size="12" font-weight="700">HTTPS Listener (Port 443) [SSL: predictoraa.com]</text>
          
          <!-- Routing Path Badges -->
          <rect x="15" y="32" width="345" height="22" rx="4" fill="#F5D0FE"/>
          <text x="22" y="47" fill="#701A75" font-size="10.5" font-weight="700">Path Rule: /chat*, /products*, /health*, /auth*</text>
          <text x="368" y="47" fill="#0369A1" font-size="11" font-weight="700">➔ tg-fashion-backend (Port 8000)</text>

          <rect x="540" y="32" width="95" height="22" rx="4" fill="#E0F2FE"/>
          <text x="547" y="47" fill="#0369A1" font-size="10.5" font-weight="700">Default Rule: /*</text>
          <text x="642" y="47" fill="#15803D" font-size="11" font-weight="700">➔ tg-frontend (Port 80)</text>
        </g>
      </g>

      <!-- ECS Cluster: fashion-agent-cluster -->
      <g transform="translate(40, 275)">
        <rect width="1110" height="405" rx="10" fill="#FFFFFF" stroke="#FF9900" stroke-width="2.5" filter="url(#shadow)"/>
        
        <!-- Cluster Header -->
        <rect x="20" y="15" width="40" height="40" rx="8" fill="#FFEDD5"/>
        <text x="40" y="42" font-size="20" text-anchor="middle">📦</text>
        <text x="70" y="32" fill="#0F172A" font-size="16" font-weight="800">Amazon ECS Fargate Cluster (fashion-agent-cluster)</text>
        <text x="70" y="50" fill="#64748B" font-size="12">Serverless MicroVMs | Security Group: <tspan fill="#DC2626" font-weight="600">ecs-tasks-sg</tspan> (Inbound Ports 80, 8000 from alb-sg only)</text>

        <!-- Subnet A: Frontend Service -->
        <g transform="translate(30, 75)">
          <rect width="490" height="305" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="1.5"/>
          <rect x="15" y="-10" width="220" height="20" rx="4" fill="#16A34A"/>
          <text x="125" y="4" fill="#FFFFFF" font-size="10" font-weight="700" text-anchor="middle">Public Subnet: ap-south-1a</text>

          <!-- Frontend Service Card -->
          <g transform="translate(15, 25)">
            <rect width="460" height="260" rx="8" fill="#FFFFFF" stroke="#86EFAC" stroke-width="1.5" filter="url(#shadow)"/>
            <text x="20" y="30" fill="#166534" font-size="14" font-weight="800">🌐 Service: fashion-frontend-service</text>
            <text x="20" y="48" fill="#64748B" font-size="11">Target Group: <tspan fill="#0F172A" font-weight="600">tg-fashion-frontend</tspan> | Desired: 1 Task</text>

            <!-- Container Details -->
            <rect x="15" y="65" width="430" height="175" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>
            <rect x="25" y="78" width="30" height="30" rx="6" fill="#E0F2FE"/>
            <text x="40" y="99" font-size="16" text-anchor="middle">🐳</text>
            <text x="65" y="92" fill="#0F172A" font-size="13" font-weight="700">Nginx Alpine Container (Port 80)</text>
            <text x="65" y="108" fill="#0284C7" font-size="11" font-weight="600">Image: fashion-frontend:latest</text>

            <line x1="25" y1="120" x2="435" y2="120" stroke="#E2E8F0" stroke-width="1"/>
            <text x="25" y="140" fill="#334155" font-size="11">• Serves Luxury Single Page Application (HTML / CSS / JS)</text>
            <text x="25" y="158" fill="#334155" font-size="11">• Multi-User Profile Switcher (Priya, Aisha, Riya)</text>
            <text x="25" y="176" fill="#334155" font-size="11">• Gzip Compression &amp; Static Asset Caching</text>
            <text x="25" y="196" fill="#166534" font-size="11" font-weight="600">Compute Sizing: 0.25 vCPU · 512 MB RAM (Serverless)</text>
            <text x="25" y="214" fill="#64748B" font-size="10.5">Logs Stream to: /ecs/fashion-frontend</text>
          </g>
        </g>

        <!-- Subnet B: Backend Service -->
        <g transform="translate(550, 75)">
          <rect width="530" height="305" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.5"/>
          <rect x="15" y="-10" width="220" height="20" rx="4" fill="#2563EB"/>
          <text x="125" y="4" fill="#FFFFFF" font-size="10" font-weight="700" text-anchor="middle">Public Subnet: ap-south-1b</text>

          <!-- Backend Service Card -->
          <g transform="translate(15, 25)">
            <rect width="500" height="260" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5" filter="url(#shadow)"/>
            <text x="20" y="30" fill="#1E40AF" font-size="14" font-weight="800">⚙️ Service: fashion-backend-service</text>
            <text x="20" y="48" fill="#64748B" font-size="11">Target Group: <tspan fill="#0F172A" font-weight="600">tg-fashion-backend</tspan> | Port 8000 | Health: /health</text>

            <!-- Container Details -->
            <rect x="15" y="65" width="470" height="175" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>
            <rect x="25" y="78" width="30" height="30" rx="6" fill="#FFEDD5"/>
            <text x="40" y="99" font-size="16" text-anchor="middle">🐍</text>
            <text x="65" y="92" fill="#0F172A" font-size="13" font-weight="700">FastAPI Application (Python 3.12 · Uvicorn)</text>
            <text x="65" y="108" fill="#EA580C" font-size="11" font-weight="600">Image: fashion-backend:latest</text>

            <line x1="25" y1="120" x2="475" y2="120" stroke="#E2E8F0" stroke-width="1"/>
            <text x="25" y="138" fill="#334155" font-size="11">• STELLA LangChain ReAct Agent &amp; SQL Query Generator</text>
            <text x="25" y="156" fill="#334155" font-size="11">• JWT Token Authentication &amp; Multi-Tier Verification</text>
            <text x="25" y="174" fill="#B45309" font-size="11" font-weight="700">⚡ Auto-Scaling Active: Target 70% CPU (1 to 5 Tasks)</text>
            <text x="25" y="194" fill="#1E40AF" font-size="11" font-weight="600">Compute Sizing: 0.5 vCPU · 1024 MB RAM (Serverless)</text>
            <text x="25" y="214" fill="#64748B" font-size="10.5">Logs Stream to: /ecs/fashion-backend (Live Tail)</text>
          </g>
        </g>
      </g>
    </g>
  </g>

  <!-- ==================== RIGHT COLUMN: GITHUB ACTIONS CI/CD & LOCAL ==================== -->
  <g transform="translate(1530, 115)">
    <rect width="430" height="375" rx="12" fill="#FFFFFF" stroke="#24292E" stroke-width="2" filter="url(#shadow)"/>
    
    <!-- Header -->
    <rect x="20" y="15" width="40" height="40" rx="8" fill="#24292E"/>
    <text x="40" y="42" font-size="22" text-anchor="middle">🐙</text>
    <text x="70" y="32" fill="#0F172A" font-size="16" font-weight="800">GitHub Actions CI/CD</text>
    <text x="70" y="50" fill="#64748B" font-size="12">Automated Deployment Workflow (.github/workflows/deploy.yml)</text>

    <!-- Step 1: Local Developer -->
    <g transform="translate(20, 75)">
      <rect width="390" height="50" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
      <text x="15" y="22" fill="#0F172A" font-size="12" font-weight="700">1. Local Workstation (Mac / Linux)</text>
      <text x="15" y="38" fill="#0284C7" font-size="11" font-weight="600">git push origin main ➔ Triggers Pipeline</text>
    </g>

    <!-- Step 2: Test & Lint -->
    <g transform="translate(20, 135)">
      <rect width="390" height="50" rx="6" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1"/>
      <text x="15" y="22" fill="#15803D" font-size="12" font-weight="700">2. CI Stage: Test &amp; Code Quality</text>
      <text x="15" y="38" fill="#166534" font-size="11">Ruff Linter &amp; Formatter + Pytest Unit Tests</text>
    </g>

    <!-- Step 3: Build & Push -->
    <g transform="translate(20, 195)">
      <rect width="390" height="50" rx="6" fill="#FFF7ED" stroke="#FDBA74" stroke-width="1"/>
      <text x="15" y="22" fill="#C2410C" font-size="12" font-weight="700">3. Docker Multi-Container Build</text>
      <text x="15" y="38" fill="#9A3412" font-size="11">Builds Nginx &amp; FastAPI ➔ Pushes to Amazon ECR</text>
    </g>

    <!-- Step 4: ECS Rolling Deploy -->
    <g transform="translate(20, 255)">
      <rect width="390" height="50" rx="6" fill="#FAF5FF" stroke="#D8B4FE" stroke-width="1"/>
      <text x="15" y="22" fill="#7E22CE" font-size="12" font-weight="700">4. CD Stage: ECS Rolling Rollout</text>
      <text x="15" y="38" fill="#6B21A8" font-size="11">Registers Task Def Revision ➔ Zero Downtime Deploy</text>
    </g>

    <!-- GitHub Secrets Banner -->
    <g transform="translate(20, 315)">
      <rect width="390" height="40" rx="6" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="1"/>
      <text x="15" y="25" fill="#991B1B" font-size="10.5" font-weight="700">🔐 Secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY</text>
    </g>
  </g>

  <!-- ==================== SUPPORTING AWS SERVICES ==================== -->
  <g transform="translate(1530, 510)">
    <rect width="430" height="365" rx="12" fill="#FFFFFF" stroke="#0284C7" stroke-width="2" filter="url(#shadow)"/>
    
    <!-- Header -->
    <rect x="20" y="15" width="40" height="40" rx="8" fill="#E0F2FE"/>
    <text x="40" y="42" font-size="20" text-anchor="middle">🛡️</text>
    <text x="70" y="32" fill="#0F172A" font-size="16" font-weight="800">AWS Supporting Services</text>
    <text x="70" y="50" fill="#64748B" font-size="12">Security, Registry &amp; Observability</text>

    <!-- 1. Amazon ECR -->
    <g transform="translate(20, 70)">
      <rect width="390" height="60" rx="6" fill="#FFF7ED" stroke="#FDBA74" stroke-width="1"/>
      <text x="15" y="24" fill="#C2410C" font-size="12" font-weight="700">📦 Amazon ECR (Private Registries)</text>
      <text x="15" y="42" fill="#9A3412" font-size="11">493116771407.dkr.ecr.ap-south-1.amazonaws.com/...</text>
    </g>

    <!-- 2. SSM Parameter Store -->
    <g transform="translate(20, 140)">
      <rect width="390" height="60" rx="6" fill="#FDF4FF" stroke="#F0ABFC" stroke-width="1"/>
      <text x="15" y="24" fill="#86198F" font-size="12" font-weight="700">🔐 AWS SSM Parameter Store</text>
      <text x="15" y="42" fill="#701A75" font-size="11">Encrypted DB Passwords &amp; SenseNova API Keys</text>
    </g>

    <!-- 3. CloudWatch Logs -->
    <g transform="translate(20, 210)">
      <rect width="390" height="60" rx="6" fill="#FDF2F8" stroke="#F472B6" stroke-width="1"/>
      <text x="15" y="24" fill="#9D174D" font-size="12" font-weight="700">🪵 Amazon CloudWatch Logs</text>
      <text x="15" y="42" fill="#831843" font-size="11">Log Groups: /ecs/fashion-* (Live Tail Enabled)</text>
    </g>

    <!-- 4. IAM Task Execution Role -->
    <g transform="translate(20, 280)">
      <rect width="390" height="65" rx="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
      <text x="15" y="22" fill="#0F172A" font-size="12" font-weight="700">👤 IAM Role: ecsTaskExecutionRole</text>
      <text x="15" y="38" fill="#475569" font-size="10.5">Permissions: ECR Pull + SSM Decrypt + CloudWatch Write</text>
      <text x="15" y="52" fill="#047857" font-size="10" font-weight="600">Attached: AllowPassRoleForECS Policy</text>
    </g>
  </g>

  <!-- ==================== BOTTOM ROW: EXTERNAL CLOUD BACKENDS ==================== -->
  <g transform="translate(40, 900)">
    <rect width="1920" height="310" rx="14" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" filter="url(#shadow)"/>
    
    <!-- Header -->
    <rect x="30" y="20" width="40" height="40" rx="8" fill="#F1F5F9"/>
    <text x="50" y="47" font-size="20" text-anchor="middle">🌐</text>
    <text x="85" y="38" fill="#0F172A" font-size="18" font-weight="800">External Cloud Databases, AI Model &amp; Observability Ecosystem</text>
    <text x="85" y="56" fill="#64748B" font-size="13">External Managed Services Connected via Internet Gateway</text>

    <!-- 1. Aiven Cloud MySQL -->
    <g transform="translate(30, 80)">
      <rect width="440" height="200" rx="10" fill="#FFF1F2" stroke="#FDA4AF" stroke-width="1.5"/>
      <text x="20" y="32" fill="#BE123C" font-size="15" font-weight="800">🗄️ Aiven Cloud MySQL (Transactional)</text>
      <text x="20" y="52" fill="#9F1239" font-size="11.5" font-weight="600">Port 16512 · TLS Encrypted · Multi-AZ</text>
      <line x1="20" y1="65" x2="420" y2="65" stroke="#FECDD3" stroke-width="1"/>
      <text x="20" y="90" fill="#334155" font-size="11.5">• E-commerce Product Catalog &amp; Pricing</text>
      <text x="20" y="112" fill="#334155" font-size="11.5">• Real-Time Inventory &amp; Stock Levels</text>
      <text x="20" y="134" fill="#334155" font-size="11.5">• Customer Loyalty Tiers (Platinum / Gold)</text>
      <text x="20" y="156" fill="#334155" font-size="11.5">• Orders, Tracking &amp; Transaction History</text>
      <text x="20" y="182" fill="#BE123C" font-size="11" font-weight="700">Host: mysql-*.aivencloud.com</text>
    </g>

    <!-- 2. Supabase PostgreSQL -->
    <g transform="translate(500, 80)">
      <rect width="440" height="200" rx="10" fill="#ECFDF5" stroke="#6EE7B7" stroke-width="1.5"/>
      <text x="20" y="32" fill="#047857" font-size="15" font-weight="800">🐘 Supabase PostgreSQL (Session Memory)</text>
      <text x="20" y="52" fill="#065F46" font-size="11.5" font-weight="600">Port 5432 · IPv4 Connection Pooler (Transaction Mode)</text>
      <line x1="20" y1="65" x2="420" y2="65" stroke="#A7F3D0" stroke-width="1"/>
      <text x="20" y="90" fill="#334155" font-size="11.5">• LangGraph / LangChain Agent Checkpoints</text>
      <text x="20" y="112" fill="#334155" font-size="11.5">• Multi-Turn Conversational Memory</text>
      <text x="20" y="134" fill="#334155" font-size="11.5">• Thread-Safe Session State Isolation</text>
      <text x="20" y="156" fill="#334155" font-size="11.5">• /chat/history Checkpoint Deletion API</text>
      <text x="20" y="182" fill="#047857" font-size="11" font-weight="700">Host: aws-0-*.pooler.supabase.com</text>
    </g>

    <!-- 3. SenseNova AI LLM -->
    <g transform="translate(970, 80)">
      <rect width="440" height="200" rx="10" fill="#EEF2FF" stroke="#A5B4FC" stroke-width="1.5"/>
      <text x="20" y="32" fill="#4338CA" font-size="15" font-weight="800">🤖 SenseNova AI (LLM Reasoning Engine)</text>
      <text x="20" y="52" fill="#3730A3" font-size="11.5" font-weight="600">HTTPS API · State-of-the-Art Generative Model</text>
      <line x1="20" y1="65" x2="420" y2="65" stroke="#C7D2FE" stroke-width="1"/>
      <text x="20" y="90" fill="#334155" font-size="11.5">• Natural Language Intent &amp; Style Extraction</text>
      <text x="20" y="112" fill="#334155" font-size="11.5">• Dynamic SQL Query Planning &amp; Generation</text>
      <text x="20" y="134" fill="#334155" font-size="11.5">• High-Fashion Styling &amp; Discount Calculation</text>
      <text x="20" y="156" fill="#334155" font-size="11.5">• Multi-Modal Ready Reasoning Pipeline</text>
      <text x="20" y="182" fill="#4338CA" font-size="11" font-weight="700">Authenticated via SecureString SSM Key</text>
    </g>

    <!-- 4. LangSmith Observability -->
    <g transform="translate(1440, 80)">
      <rect width="450" height="200" rx="10" fill="#FAF5FF" stroke="#D8B4FE" stroke-width="1.5"/>
      <text x="20" y="32" fill="#7E22CE" font-size="15" font-weight="800">🔗 LangChain Ecosystem (LangSmith)</text>
      <text x="20" y="52" fill="#6B21A8" font-size="11.5" font-weight="600">Production LLM Observability &amp; Tracing</text>
      <line x1="20" y1="65" x2="430" y2="65" stroke="#E9D5FF" stroke-width="1"/>
      <text x="20" y="90" fill="#334155" font-size="11.5">• Full Execution Tree &amp; Prompt Tracing</text>
      <text x="20" y="112" fill="#334155" font-size="11.5">• Latency Breakdown per Tool &amp; Database Call</text>
      <text x="20" y="134" fill="#334155" font-size="11.5">• Token Cost Analytics &amp; Budget Monitoring</text>
      <text x="20" y="156" fill="#334155" font-size="11.5">• Hallucination &amp; Query Debugging Web UI</text>
      <text x="20" y="182" fill="#7E22CE" font-size="11" font-weight="700">Project: maison-luxe-stella</text>
    </g>
  </g>

  <!-- ==================== CONNECTING FLOW ARROWS ==================== -->
  
  <!-- Shopper to Route 53 -->
  <path d="M 130 250 L 130 300" fill="none" stroke="#00A4A6" stroke-width="2.5" marker-end="url(#arrow-green)"/>
  <path d="M 130 435 L 130 480" fill="none" stroke="#8C4FFF" stroke-width="2.5" marker-end="url(#arrow-purple)"/>

  <!-- Route 53 to ALB -->
  <path d="M 220 560 C 260 560, 260 320, 320 320" fill="none" stroke="#0284C7" stroke-width="3" marker-end="url(#arrow-blue)"/>
  
  <!-- ALB to Frontend Target Group -->
  <path d="M 570 365 L 570 415" fill="none" stroke="#16A34A" stroke-width="3" marker-end="url(#arrow-green)"/>
  
  <!-- ALB to Backend Target Group -->
  <path d="M 1090 365 L 1090 415" fill="none" stroke="#0284C7" stroke-width="3" marker-end="url(#arrow-blue)"/>

  <!-- Backend Task to External Databases -->
  <path d="M 1090 730 L 1090 850 C 1090 880, 250 860, 250 900" fill="none" stroke="#BE123C" stroke-width="2.5" stroke-dasharray="6 4" marker-end="url(#arrow-gray)"/>
  <path d="M 1090 730 L 1090 850 C 1090 880, 720 860, 720 900" fill="none" stroke="#047857" stroke-width="2.5" stroke-dasharray="6 4" marker-end="url(#arrow-gray)"/>
  <path d="M 1090 730 L 1090 850 C 1090 880, 1190 860, 1190 900" fill="none" stroke="#4338CA" stroke-width="2.5" stroke-dasharray="6 4" marker-end="url(#arrow-gray)"/>

  <!-- GitHub Actions to ECR & ECS -->
  <path d="M 1745 490 L 1745 510" fill="none" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
  <path d="M 1530 300 C 1450 300, 1450 420, 1370 420" fill="none" stroke="#EA580C" stroke-width="3" marker-end="url(#arrow-orange)"/>

</svg>
"""

def main():
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    svg_path = docs_dir / "aws_architecture_diagram.svg"
    png_path = docs_dir / "aws_architecture_diagram.png"
    jpg_path = docs_dir / "aws_architecture_diagram.jpg"

    svg_data = generate_svg()
    
    # Save SVG
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_data)
    print(f"✅ SVG Diagram generated: {svg_path}")

    # Convert SVG to High-Resolution PNG via PyMuPDF (fitz)
    doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
    page = doc[0]
    
    # Render at 2x scaling (4000x2500 px) for ultra-crisp presentation display
    pix = page.get_pixmap(dpi=192)
    pix.save(str(png_path))
    print(f"✅ PNG Diagram generated (High-Res 3840x2400): {png_path}")

    # Convert to High-Quality JPG
    img = Image.open(png_path)
    rgb_img = img.convert("RGB")
    rgb_img.save(str(jpg_path), "JPEG", quality=95)
    print(f"✅ JPG Diagram generated (High-Res Quality 95%): {jpg_path}")

if __name__ == "__main__":
    main()
