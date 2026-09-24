#!/usr/bin/env python3
"""
scripts/generate_architecture_gif.py
Generates an executive, publication-grade animated GIF visualizing the live network
and data flow during a POST /chat query in the Maison Luxé (STELLA) AWS production architecture.
"""

from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

WIDTH = 1380
HEIGHT = 740

def make_pro_frame_svg(stage: int, packet_pos=None, packet_color="#00f0ff", trail_positions=None, step_index: int = 1) -> str:
    """
    Renders an ultra-clean, enterprise-grade SVG for a specific animation step.
    """
    # Active states
    is_client_active = (stage in [0, 1, 7, 8])
    is_dns_active = (stage in [1, 2])
    is_alb_active = (stage in [2, 3, 7])
    is_alb_rule_active = (stage >= 2 and stage <= 7)
    is_be_active = (stage in [3, 4, 5, 6, 7])
    is_llm_active = (stage == 4)
    is_mysql_active = (stage == 5)
    is_supabase_active = (stage == 6)
    is_completed = (stage == 8)

    # Wire paths colors
    wire_client_dns = "#00f0ff" if stage in [1, 2] else "#233348"
    wire_dns_alb = "#00f0ff" if stage in [1, 2] else "#233348"
    wire_alb_be = "#c084fc" if stage in [3, 7] else "#233348"
    wire_be_llm = "#f43f5e" if stage == 4 else "#233348"
    wire_be_mysql = "#10b981" if stage == 5 else "#233348"
    wire_be_supabase = "#06b6d4" if stage == 6 else "#233348"

    # CPU bar
    if stage in [4, 5, 6]:
        cpu_w = 48
        cpu_text = "38%"
        cpu_fill = "#f59e0b"
    elif stage in [7, 8]:
        cpu_w = 26
        cpu_text = "20%"
        cpu_fill = "#10b981"
    else:
        cpu_w = 22
        cpu_text = "19%"
        cpu_fill = "#10b981"

    # Latency and Status
    if stage == 8:
        latency_str = "842 ms"
        latency_color = "#10b981"
        status_str = "200 OK"
        status_color = "#10b981"
    elif stage >= 4:
        latency_str = "448 ms"
        latency_color = "#38bdf8"
        status_str = "PROCESSING"
        status_color = "#f59e0b"
    elif stage >= 2:
        latency_str = "28 ms"
        latency_color = "#38bdf8"
        status_str = "ROUTING"
        status_color = "#38bdf8"
    else:
        latency_str = "0 ms"
        latency_color = "#94a3b8"
        status_str = "PENDING"
        status_color = "#94a3b8"

    cur_step = step_index

    # Status Bar info
    status_map = {
        0: ("1. INITIATION", "#0284c7", "Client sends POST /chat: &quot;Looking for a red silk evening gown under ₹20,000 for a gala&quot;"),
        1: ("2. DNS &amp; TLS", "#0284c7", "Route 53 resolves predictoraa.com &bull; AWS Certificate Manager validates *.predictoraa.com (TLS 1.3)"),
        2: ("3. ALB INGRESS", "#8b5cf6", "ALB matches path &quot;/chat&quot; &rarr; Rule 1 forwards to Target Group: tg-fashion-backend (Port 8000)"),
        3: ("4. ECS FARGATE", "#7e22ce", "FastAPI container receives request in Private Subnet (10.0.1.42) &bull; LangGraph agent activated"),
        4: ("5. SENSENOVA LLM", "#be185d", "SenseNova LLM extracts parameters (Category: Dress, MaxPrice: 20000) &amp; synthesizes SQL query"),
        5: ("6. AIVEN MYSQL", "#047857", "Executing live inventory query against Aiven Cloud MySQL (Port 16512 TLS) &bull; 3 rows returned (38ms)"),
        6: ("7. SUPABASE STATE", "#0f766e", "Serializing conversation turn &amp; persisting state checkpoint to Supabase PostgreSQL (thread_id: usr_priya)"),
        7: ("8. RESPONSE EGRESS", "#0284c7", "Backend returns AI styling payload JSON back through Application Load Balancer to Client"),
        8: ("9. COMPLETED 200 OK", "#10b981", "Client renders STELLA styling recommendation with Ruby Red Silk Gown &amp; VIP Platinum discount (842ms)")
    }
    pill_label, pill_color, status_desc = status_map.get(stage, status_map[0])

    # Mobile Chat View states
    show_user_bubble = (stage >= 0)
    show_typing_indicator = (stage >= 2 and stage <= 6)
    show_ai_response = (stage >= 7)

    # Render trail dots if present
    trail_svg = ""
    if trail_positions:
        for i, (tx, ty) in enumerate(trail_positions):
            alpha = (i + 1) / (len(trail_positions) + 1.0)
            rad = 2.5 + alpha * 3.5
            trail_svg += f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{rad:.1f}" fill="{packet_color}" opacity="{alpha*0.6:.2f}"/>'

    packet_svg = ""
    if packet_pos:
        px, py = packet_pos
        packet_svg = f"""
        <g>
          {trail_svg}
          <circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="{packet_color}" opacity="0.3" filter="url(#core-glow)"/>
          <circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="{packet_color}" filter="url(#core-glow)"/>
          <circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#ffffff"/>
        </g>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" style="background:#090d16; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Gradients -->
    <linearGradient id="topNavGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#141e33"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>

    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#141c2d"/>
      <stop offset="100%" stop-color="#0e1524"/>
    </linearGradient>

    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>

    <!-- Filters -->
    <filter id="core-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{packet_color}" flood-opacity="0.9"/>
    </filter>

    <filter id="box-cyan" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#00f0ff" flood-opacity="0.6"/>
    </filter>

    <filter id="box-purple" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#c084fc" flood-opacity="0.6"/>
    </filter>

    <filter id="box-green" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#10b981" flood-opacity="0.6"/>
    </filter>

    <filter id="box-pink" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#f43f5e" flood-opacity="0.6"/>
    </filter>
  </defs>

  <!-- ==================== HEADER BAR ==================== -->
  <rect x="0" y="0" width="{WIDTH}" height="60" fill="url(#topNavGrad)" stroke="#1e293b" stroke-width="1"/>
  
  <!-- Brand Icon -->
  <rect x="18" y="11" width="38" height="38" rx="8" fill="url(#goldGrad)"/>
  <text x="37" y="36" fill="#ffffff" font-size="20" font-weight="900" text-anchor="middle">M</text>

  <!-- Title & Meta -->
  <text x="68" y="28" fill="#ffffff" font-size="15" font-weight="800" letter-spacing="-0.3">MAISON LUXÉ <tspan fill="#f59e0b">// STELLA AI</tspan> <tspan fill="#94a3b8" font-size="12" font-weight="500">| AWS Live Traffic Trace: POST /chat</tspan></text>
  <text x="68" y="46" fill="#64748b" font-size="10.5" font-family="monospace">Topology: Route 53 &bull; ALB (Dual-AZ) &bull; ECS Fargate Serverless &bull; SenseNova LLM &bull; Aiven MySQL &bull; Supabase</text>

  <!-- Badges Top Right -->
  <g transform="translate(860, 15)">
    <rect width="130" height="28" rx="6" fill="#131d2e" stroke="#334155" stroke-width="1"/>
    <circle cx="14" cy="14" r="3.5" fill="#10b981"/>
    <text x="24" y="18" fill="#cbd5e1" font-size="10" font-family="monospace" font-weight="600">us-east-1a OK</text>
  </g>

  <g transform="translate(1000, 15)">
    <rect width="175" height="28" rx="6" fill="#064e3b" stroke="#10b981" stroke-width="1"/>
    <text x="14" y="18" fill="#34d399" font-size="10.5" font-family="monospace" font-weight="700">🔒 predictoraa.com</text>
  </g>

  <g transform="translate(1185, 15)">
    <rect width="175" height="28" rx="6" fill="#1e1b4b" stroke="#6366f1" stroke-width="1"/>
    <text x="12" y="18" fill="#c7d2fe" font-size="10" font-weight="700">👑 Priya (VIP Platinum)</text>
  </g>

  <!-- ==================== SUB-HEADER: ARCHITECTURAL PIPELINE BREADCRUMB ==================== -->
  <rect x="0" y="60" width="{WIDTH}" height="36" fill="#0b101c" stroke="#1e293b" stroke-width="1"/>
  
  <g transform="translate(18, 68)" font-size="10" font-weight="600">
    <text x="0" y="14" fill="#64748b" font-weight="700">PIPELINE:</text>
    
    <text x="70" y="14" fill="{'#00f0ff' if cur_step==1 else '#64748b'}" font-weight="{'800' if cur_step==1 else '600'}">1. Client Request</text>
    <text x="175" y="14" fill="#334155">&rarr;</text>
    
    <text x="195" y="14" fill="{'#00f0ff' if cur_step==2 else '#64748b'}" font-weight="{'800' if cur_step==2 else '600'}">2. Route 53 / SSL</text>
    <text x="305" y="14" fill="#334155">&rarr;</text>
    
    <text x="325" y="14" fill="{'#c084fc' if cur_step==3 else '#64748b'}" font-weight="{'800' if cur_step==3 else '600'}">3. ALB Path Routing</text>
    <text x="445" y="14" fill="#334155">&rarr;</text>
    
    <text x="465" y="14" fill="{'#c084fc' if cur_step==4 else '#64748b'}" font-weight="{'800' if cur_step==4 else '600'}">4. ECS Fargate Backend</text>
    <text x="595" y="14" fill="#334155">&rarr;</text>
    
    <text x="615" y="14" fill="{'#f43f5e' if cur_step==5 else '#64748b'}" font-weight="{'800' if cur_step==5 else '600'}">5. SenseNova LLM</text>
    <text x="730" y="14" fill="#334155">&rarr;</text>
    
    <text x="750" y="14" fill="{'#10b981' if cur_step==6 else '#64748b'}" font-weight="{'800' if cur_step==6 else '600'}">6. Aiven MySQL</text>
    <text x="840" y="14" fill="#334155">&rarr;</text>
    
    <text x="860" y="14" fill="{'#06b6d4' if cur_step==7 else '#64748b'}" font-weight="{'800' if cur_step==7 else '600'}">7. Supabase Memory</text>
    <text x="980" y="14" fill="#334155">&rarr;</text>
    
    <text x="1000" y="14" fill="{'#10b981' if cur_step==8 else '#64748b'}" font-weight="{'800' if cur_step==8 else '600'}">8. Response 200 OK</text>
  </g>

  <!-- ==================== LEFT ARCHITECTURE CANVAS (VPC & CLOUD) ==================== -->
  
  <!-- Outer VPC Perimeter Box -->
  <rect x="18" y="106" width="875" height="576" rx="12" fill="#090d16" stroke="#25354c" stroke-dasharray="5 4" stroke-width="1.2"/>
  <rect x="30" y="96" width="220" height="20" rx="4" fill="#131d2e" stroke="#334155" stroke-width="1"/>
  <text x="40" y="110" fill="#94a3b8" font-size="9.5" font-family="monospace" font-weight="700">AWS VPC (10.0.0.0/16) - us-east-1</text>

  <!-- ECS Cluster Boundary Box -->
  <rect x="365" y="135" width="265" height="525" rx="10" fill="#0b1220" stroke="#f59e0b" stroke-dasharray="6 3" stroke-width="1.2"/>
  <rect x="375" y="125" width="225" height="20" rx="4" fill="#1c160c" stroke="#f59e0b" stroke-width="1"/>
  <text x="385" y="139" fill="#f59e0b" font-size="9.5" font-weight="700">AWS ECS (fashion-agent-cluster)</text>

  <!-- ==================== CONNECTOR PATHS ==================== -->
  <!-- Path: Client -> Route 53 -->
  <path d="M 98 245 L 140 245" fill="none" stroke="{wire_client_dns}" stroke-width="3" stroke-linecap="round"/>
  
  <!-- Path: Route 53 -> ALB -->
  <path d="M 215 245 L 255 245" fill="none" stroke="{wire_dns_alb}" stroke-width="3" stroke-linecap="round"/>

  <!-- Path: ALB -> Frontend (Idle during POST /chat) -->
  <path d="M 345 225 C 365 225, 375 200, 385 200" fill="none" stroke="#1c2637" stroke-width="2"/>

  <!-- Path: ALB -> Backend Task 1 (Active) -->
  <path d="M 345 255 C 365 255, 375 315, 385 315" fill="none" stroke="{wire_alb_be}" stroke-width="3.5" stroke-linecap="round"/>

  <!-- Path: Backend -> SenseNova LLM -->
  <path d="M 610 295 C 655 295, 680 195, 715 195" fill="none" stroke="{wire_be_llm}" stroke-width="3" stroke-linecap="round"/>

  <!-- Path: Backend -> Aiven MySQL -->
  <path d="M 610 325 C 655 325, 680 325, 715 325" fill="none" stroke="{wire_be_mysql}" stroke-width="3" stroke-linecap="round"/>

  <!-- Path: Backend -> Supabase Postgres -->
  <path d="M 610 355 C 655 355, 680 455, 715 455" fill="none" stroke="{wire_be_supabase}" stroke-width="3" stroke-linecap="round"/>

  <!-- ==================== ARCHITECTURE NODES ==================== -->

  <!-- 1. Client Node -->
  <g transform="translate(30, 195)" {"filter='url(#box-cyan)'" if is_client_active else ""}>
    <rect width="68" height="100" rx="8" fill="url(#cardGrad)" stroke="{'#00f0ff' if is_client_active else '#334155'}" stroke-width="{'2' if is_client_active else '1'}"/>
    <rect width="68" height="22" rx="7" fill="#0284c7"/>
    <text x="34" y="15" fill="#ffffff" font-size="9" font-weight="800" text-anchor="middle">CLIENT</text>
    <text x="34" y="42" fill="#f8fafc" font-size="9.5" font-weight="700" text-anchor="middle">Browser</text>
    <text x="34" y="58" fill="#94a3b8" font-size="7.5" font-family="monospace" text-anchor="middle">predictoraa</text>
    <text x="34" y="72" fill="#38bdf8" font-size="7" font-weight="600" text-anchor="middle">Port 443 HTTPS</text>
    <rect x="7" y="80" width="54" height="14" rx="3" fill="#1e293b"/>
    <text x="34" y="90" fill="#10b981" font-size="7" font-weight="700" font-family="monospace" text-anchor="middle">POST /chat</text>
  </g>

  <!-- 2. Route 53 + ACM Node -->
  <g transform="translate(140, 195)" {"filter='url(#box-cyan)'" if is_dns_active else ""}>
    <rect width="75" height="100" rx="8" fill="url(#cardGrad)" stroke="{'#00f0ff' if is_dns_active else '#334155'}" stroke-width="{'2' if is_dns_active else '1'}"/>
    <rect width="75" height="22" rx="7" fill="#1e293b"/>
    <text x="37" y="15" fill="#38bdf8" font-size="8.5" font-weight="800" text-anchor="middle">ROUTE 53</text>
    <text x="37" y="42" fill="#f8fafc" font-size="9" font-weight="700" text-anchor="middle">DNS Alias</text>
    <text x="37" y="56" fill="#94a3b8" font-size="7.5" font-family="monospace" text-anchor="middle">ACM SSL</text>
    <text x="37" y="70" fill="#10b981" font-size="7.5" font-weight="600" text-anchor="middle">TLS 1.3 Certified</text>
    <text x="37" y="85" fill="#64748b" font-size="7" text-anchor="middle">*.predictoraa</text>
  </g>

  <!-- 3. ALB Node -->
  <g transform="translate(255, 175)" {"filter='url(#box-purple)'" if is_alb_active else ""}>
    <rect width="90" height="135" rx="8" fill="url(#cardGrad)" stroke="{'#c084fc' if is_alb_active else '#334155'}" stroke-width="{'2' if is_alb_active else '1'}"/>
    <rect width="90" height="22" rx="7" fill="#0284c7"/>
    <text x="45" y="15" fill="#ffffff" font-size="9" font-weight="800" text-anchor="middle">AWS ALB</text>
    <text x="45" y="40" fill="#f8fafc" font-size="9" font-weight="700" text-anchor="middle">alb-fashion</text>
    
    <!-- Rule 1: Frontend -->
    <rect x="5" y="48" width="80" height="18" rx="3" fill="#0a0f18" stroke="#1e293b"/>
    <text x="8" y="60" fill="#64748b" font-size="7" font-family="monospace">/* &rarr; TG:FE:80</text>

    <!-- Rule 2: Backend Chat (DYNAMIC MATCH) -->
    <rect x="5" y="72" width="80" height="26" rx="4" fill="{'#2c154a' if is_alb_rule_active else '#0a0f18'}" stroke="{'#c084fc' if is_alb_rule_active else '#1e293b'}" stroke-width="{'1.5' if is_alb_rule_active else '1'}"/>
    <text x="8" y="84" fill="{'#e9d5ff' if is_alb_rule_active else '#94a3b8'}" font-size="7" font-family="monospace" font-weight="700">/chat* &rarr; BE:8000</text>
    <text x="8" y="94" fill="{'#38bdf8' if is_alb_rule_active else '#64748b'}" font-size="6.5" font-family="monospace">Rule 1 Matched</text>

    <text x="45" y="118" fill="#10b981" font-size="7" font-weight="600" text-anchor="middle">● Dual-AZ Health: OK</text>
  </g>

  <!-- 4A. Frontend Task (Nginx) -->
  <g transform="translate(385, 160)">
    <rect width="225" height="70" rx="8" fill="#0d1424" stroke="#25354c" stroke-width="1"/>
    <rect width="225" height="18" rx="7" fill="#0369a1"/>
    <text x="112" y="13" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">fashion-frontend-service (Port 80)</text>
    <text x="10" y="34" fill="#38bdf8" font-size="8.5" font-weight="700">Container: Nginx Alpine (Public Proxy)</text>
    <text x="10" y="47" fill="#64748b" font-size="7.5">Serves: Luxury Catalog HTML5, CSS3, React Bundle</text>
    <text x="10" y="60" fill="#10b981" font-size="7.5" font-weight="600">Private Subnet: 10.0.1.12 &bull; Latency: 12ms</text>
  </g>

  <!-- 4B. Backend Task 1 (FastAPI + LangGraph) ACTIVE -->
  <g transform="translate(385, 255)" {"filter='url(#box-purple)'" if is_be_active else ""}>
    <rect width="225" height="120" rx="8" fill="#151128" stroke="{'#c084fc' if is_be_active else '#334155'}" stroke-width="{'2' if is_be_active else '1'}"/>
    <rect width="225" height="20" rx="7" fill="#7e22ce"/>
    <text x="112" y="14" fill="#ffffff" font-size="9" font-weight="800" text-anchor="middle">fashion-backend-service (Task 1)</text>
    <text x="10" y="36" fill="#c084fc" font-size="9" font-weight="800">FastAPI + LangGraph Agent (:8000)</text>
    <text x="10" y="50" fill="#cbd5e1" font-size="7.5">Modules: JWT Auth &bull; SQL Agent Tool &bull; Checkpoints</text>
    
    <!-- CPU Usage Meter -->
    <text x="10" y="65" fill="#94a3b8" font-size="7.5">Fargate CPU Usage:</text>
    <rect x="95" y="58" width="90" height="7" rx="3.5" fill="#1e293b"/>
    <rect x="95" y="58" width="{cpu_w}" height="7" rx="3.5" fill="{cpu_fill}"/>
    <text x="192" y="65" fill="#ffffff" font-size="7.5" font-family="monospace">{cpu_text}</text>

    <!-- Subnet & IP Info -->
    <text x="10" y="82" fill="#38bdf8" font-size="7.5" font-family="monospace">Subnet: 10.0.1.42 (us-east-1a) &bull; 0.5 vCPU / 1GB</text>
    
    <rect x="10" y="92" width="205" height="18" rx="4" fill="#221938" stroke="#4c1d95"/>
    <text x="14" y="104" fill="#34d399" font-size="7" font-family="monospace">● TaskID: ecs-task-8a9f2 (HEALTHY 200)</text>
  </g>

  <!-- 4C. Backend Task 2 (Auto-Scaling Replica - Standby) -->
  <g transform="translate(385, 395)" opacity="0.45">
    <rect width="225" height="75" rx="8" fill="#0d1424" stroke="#475569" stroke-dasharray="3 3" stroke-width="1"/>
    <rect width="225" height="18" rx="7" fill="#4c1d95"/>
    <text x="112" y="13" fill="#e9d5ff" font-size="8.5" font-weight="700" text-anchor="middle">fashion-backend-service (Task 2 Replica)</text>
    <text x="10" y="34" fill="#94a3b8" font-size="8">Auto-Scaling Policy: Target Tracking (CPU &gt; 70%)</text>
    <text x="10" y="48" fill="#64748b" font-size="7.5">DesiredCount: 1 &bull; MinCapacity: 1 &bull; MaxCapacity: 3</text>
    <text x="10" y="62" fill="#64748b" font-size="7" font-family="monospace">Standby Mode (Subnet us-east-1b)</text>
  </g>

  <!-- 5A. SenseNova LLM Node -->
  <g transform="translate(715, 150)" {"filter='url(#box-pink)'" if is_llm_active else ""}>
    <rect width="165" height="90" rx="8" fill="#1b0f1a" stroke="{'#f43f5e' if is_llm_active else '#334155'}" stroke-width="{'2' if is_llm_active else '1'}"/>
    <rect width="165" height="20" rx="7" fill="#be185d"/>
    <text x="82" y="14" fill="#ffffff" font-size="9" font-weight="800" text-anchor="middle">SenseNova LLM API</text>
    <text x="10" y="35" fill="#f472b6" font-size="9" font-weight="700">SenseChat-5 (128k)</text>
    <text x="10" y="48" fill="#94a3b8" font-size="7.5" font-family="monospace">HTTPS External Gateway</text>
    <text x="10" y="60" fill="#cbd5e1" font-size="7.5">Intent + Parameterized SQL Synthesis</text>
    
    <rect x="8" y="68" width="149" height="16" rx="3" fill="#2d1326"/>
    <text x="12" y="79" fill="#fda4af" font-size="7" font-family="monospace">SQL: category='Dress' &amp; price&lt;=20k</text>
  </g>

  <!-- 5B. Aiven Cloud MySQL Node -->
  <g transform="translate(715, 275)" {"filter='url(#box-green)'" if is_mysql_active else ""}>
    <rect width="165" height="100" rx="8" fill="#0d1f18" stroke="{'#10b981' if is_mysql_active else '#334155'}" stroke-width="{'2' if is_mysql_active else '1'}"/>
    <rect width="165" height="20" rx="7" fill="#047857"/>
    <text x="82" y="14" fill="#ffffff" font-size="9" font-weight="800" text-anchor="middle">Aiven Cloud MySQL</text>
    <text x="10" y="36" fill="#34d399" font-size="9" font-weight="700">Catalog &amp; Inventory DB</text>
    <text x="10" y="49" fill="#94a3b8" font-size="7.5" font-family="monospace">Port 16512 (TLS Encrypted)</text>
    <text x="10" y="62" fill="#cbd5e1" font-size="7.5">Products, Stock, Sizes, Prices</text>
    
    <rect x="8" y="72" width="149" height="20" rx="3" fill="#132c22"/>
    <text x="12" y="85" fill="#6ee7b7" font-size="7" font-family="monospace">Returned: 3 rows &bull; Latency: 38ms</text>
  </g>

  <!-- 5C. Supabase PostgreSQL Node -->
  <g transform="translate(715, 410)" {"filter='url(#box-cyan)'" if is_supabase_active else ""}>
    <rect width="165" height="95" rx="8" fill="#0c1d22" stroke="{'#06b6d4' if is_supabase_active else '#334155'}" stroke-width="{'2' if is_supabase_active else '1'}"/>
    <rect width="165" height="20" rx="7" fill="#0f766e"/>
    <text x="82" y="14" fill="#ffffff" font-size="9" font-weight="800" text-anchor="middle">Supabase PostgreSQL</text>
    <text x="10" y="36" fill="#2dd4bf" font-size="9" font-weight="700">LangGraph Checkpointer</text>
    <text x="10" y="49" fill="#94a3b8" font-size="7.5" font-family="monospace">Port 5432 (Session Pooler)</text>
    <text x="10" y="62" fill="#cbd5e1" font-size="7.5">Multi-Turn Thread Isolation</text>
    
    <rect x="8" y="70" width="149" height="18" rx="3" fill="#132a30"/>
    <text x="12" y="82" fill="#67e8f9" font-size="7" font-family="monospace">Commit checkpoint: thread_usr_01</text>
  </g>

  <!-- Dynamic Moving Packet Element -->
  {packet_svg}

  <!-- ==================== RIGHT SIDE PANEL (PHONE & LOGS) ==================== -->
  
  <!-- Right Container Border -->
  <rect x="910" y="106" width="452" height="576" rx="12" fill="#0d1424" stroke="#1e293b" stroke-width="1"/>

  <!-- Telemetry HUD Bar (Top Right) -->
  <g transform="translate(922, 116)">
    <rect width="102" height="46" rx="6" fill="#141d2f" stroke="#334155" stroke-width="1"/>
    <text x="10" y="15" fill="#94a3b8" font-size="7.5" font-weight="700">TOTAL LATENCY</text>
    <text x="10" y="35" fill="{latency_color}" font-size="14" font-weight="900" font-family="monospace">{latency_str}</text>

    <rect x="110" y="0" width="102" height="46" rx="6" fill="#141d2f" stroke="#334155" stroke-width="1"/>
    <text x="120" y="15" fill="#94a3b8" font-size="7.5" font-weight="700">STATUS CODE</text>
    <text x="120" y="35" fill="{status_color}" font-size="14" font-weight="900" font-family="monospace">{status_str}</text>

    <rect x="220" y="0" width="102" height="46" rx="6" fill="#141d2f" stroke="#334155" stroke-width="1"/>
    <text x="230" y="15" fill="#94a3b8" font-size="7.5" font-weight="700">BACKEND CPU</text>
    <text x="230" y="35" fill="{cpu_fill}" font-size="14" font-weight="900" font-family="monospace">{cpu_text}</text>

    <rect x="330" y="0" width="98" height="46" rx="6" fill="#141d2f" stroke="#334155" stroke-width="1"/>
    <text x="340" y="15" fill="#94a3b8" font-size="7.5" font-weight="700">FARGATE TASKS</text>
    <text x="340" y="35" fill="#38bdf8" font-size="14" font-weight="900" font-family="monospace">2 Active</text>
  </g>

  <!-- Smartphone Mockup Frame -->
  <g transform="translate(922, 172)" {"filter='url(#box-green)'" if is_completed else ""}>
    <rect width="428" height="328" rx="14" fill="#080c14" stroke="{'#10b981' if is_completed else '#25354c'}" stroke-width="{'1.8' if is_completed else '1.5'}"/>
    
    <!-- Phone Top Status Bar -->
    <rect width="428" height="26" rx="13" fill="#161f30"/>
    <text x="20" y="17" fill="#cbd5e1" font-size="9" font-weight="600">09:41</text>
    
    <!-- Speaker & Camera notch -->
    <rect x="180" y="6" width="68" height="6" rx="3" fill="#080c14"/>
    <circle cx="258" cy="9" r="2.5" fill="#1e293b"/>

    <text x="408" y="17" fill="#cbd5e1" font-size="8.5" font-family="monospace" text-anchor="end">5G &bull; 100%</text>

    <!-- Browser URL Bar -->
    <rect x="10" y="32" width="408" height="22" rx="5" fill="#0f172a" stroke="#1e293b"/>
    <circle cx="24" cy="43" r="3" fill="#10b981"/>
    <text x="34" y="46" fill="#38bdf8" font-size="8.5" font-family="monospace">https://predictoraa.com/chat</text>
    <text x="398" y="46" fill="#64748b" font-size="8" text-anchor="end">🔒 SSL 256-bit</text>

    <!-- Chat Messages Viewport -->
    <!-- Initial Bot Welcome -->
    <rect x="14" y="62" width="290" height="28" rx="8" fill="#141c2d" stroke="#283548"/>
    <text x="22" y="75" fill="#f59e0b" font-size="8" font-weight="700">STELLA AI Boutique:</text>
    <text x="22" y="85" fill="#94a3b8" font-size="8">Welcome to Maison Luxé! How may I curate your look today?</text>

    <!-- User Query Bubble -->
    {f'''
    <g>
      <rect x="120" y="98" width="294" height="34" rx="8" fill="#0284c7"/>
      <text x="130" y="112" fill="#ffffff" font-size="8" font-weight="700">Priya Sharma (VIP Platinum &bull; 15% Off):</text>
      <text x="130" y="125" fill="#e0f2fe" font-size="8">Looking for a red silk evening gown under ₹20,000 for a gala</text>
    </g>
    ''' if show_user_bubble else ''}

    <!-- Typing Spinner -->
    {f'''
    <g>
      <rect x="14" y="140" width="210" height="24" rx="8" fill="#1e1830" stroke="#a855f7" stroke-width="1"/>
      <circle cx="30" cy="152" r="3" fill="#c084fc"/>
      <circle cx="40" cy="152" r="3" fill="#c084fc"/>
      <circle cx="50" cy="152" r="3" fill="#c084fc"/>
      <text x="65" y="156" fill="#e9d5ff" font-size="8" font-weight="600">STELLA querying databases &amp; LLM...</text>
    </g>
    ''' if show_typing_indicator else ''}

    <!-- AI Response Card with Product -->
    {f'''
    <g>
      <!-- Bot Message text -->
      <rect x="14" y="138" width="370" height="24" rx="6" fill="#141c2d"/>
      <text x="22" y="153" fill="#e2e8f0" font-size="8">I have selected an exquisite masterpiece that meets your exact criteria:</text>

      <!-- Luxury Product Recommendation Card -->
      <rect x="14" y="168" width="400" height="115" rx="8" fill="#101726" stroke="#2563eb" stroke-width="1.4"/>
      
      <!-- Thumbnail with dress silhouette badge -->
      <rect x="24" y="178" width="70" height="95" rx="6" fill="#881337" stroke="#be123c"/>
      <text x="59" y="222" fill="#fecdd3" font-size="9" font-weight="800" text-anchor="middle">👗 SILK</text>
      <text x="59" y="235" fill="#fda4af" font-size="7.5" text-anchor="middle">GOWN</text>

      <!-- Details -->
      <text x="105" y="193" fill="#ffffff" font-size="10" font-weight="800">Ruby Red Silk Crêpe Evening Gown</text>
      <text x="105" y="206" fill="#94a3b8" font-size="8">Maison Luxé Autumn Atelier &bull; Micro-Pleated Drape</text>
      
      <text x="105" y="224" fill="#38bdf8" font-size="11" font-weight="800">₹18,500 <tspan fill="#64748b" font-size="8.5" font-weight="normal" text-decoration="line-through">₹22,000</tspan></text>
      
      <!-- VIP Discount Badge -->
      <rect x="105" y="232" width="165" height="18" rx="4" fill="#064e3b" stroke="#10b981"/>
      <text x="112" y="244" fill="#34d399" font-size="7.5" font-weight="700">👑 VIP Platinum: -15% Applied (-₹2,775)</text>
      <text x="280" y="244" fill="#6ee7b7" font-size="8" font-weight="800">Net: ₹15,725</text>
      
      <circle cx="110" cy="265" r="3" fill="#10b981"/>
      <text x="118" y="268" fill="#10b981" font-size="8" font-weight="600">Verified In Stock: 4 units (Aiven MySQL)</text>
    </g>
    ''' if show_ai_response else ''}

    <!-- Bottom Input Bar -->
    <rect x="10" y="292" width="408" height="28" rx="7" fill="#111827" stroke="#25354c"/>
    <text x="22" y="310" fill="#64748b" font-size="8">Ask STELLA any question or browse collection...</text>
    <rect x="365" y="296" width="46" height="20" rx="4" fill="#0284c7"/>
    <text x="388" y="309" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle">Send</text>
  </g>

  <!-- Live CloudWatch Logs (Bottom Right) -->
  <g transform="translate(922, 510)">
    <rect width="428" height="162" rx="8" fill="#05080e" stroke="#1e293b" stroke-width="1"/>
    <text x="14" y="16" fill="#64748b" font-size="8" font-weight="700" font-family="monospace">AWS CLOUDWATCH LOGS &amp; TRACE ENGINE</text>
    
    <text x="14" y="34" fill="#38bdf8" font-size="7.5" font-family="monospace">[14:20:02.102] [ALB:443] Path /chat &rarr; rule 1 matched (tg-fashion-backend)</text>
    <text x="14" y="48" fill="#c084fc" font-size="7.5" font-family="monospace">[14:20:02.115] [ECS:FASTAPI] POST /chat token auth valid (VIP: Platinum)</text>
    {f'''<text x="14" y="62" fill="#f43f5e" font-size="7.5" font-family="monospace">[14:20:02.525] [AI:SENSENOVA] SQL synthesized in 410ms (128 tokens)</text>''' if stage >= 4 else ''}
    {f'''<text x="14" y="76" fill="#10b981" font-size="7.5" font-family="monospace">[14:20:02.563] [DB:AIVEN] Executed SELECT in 38ms (3 items in stock)</text>''' if stage >= 5 else ''}
    {f'''<text x="14" y="90" fill="#06b6d4" font-size="7.5" font-family="monospace">[14:20:02.587] [DB:SUPABASE] Checkpoint committed for thread_id 'usr_priya'</text>''' if stage >= 6 else ''}
    {f'''<text x="14" y="104" fill="#10b981" font-size="7.5" font-family="monospace">[14:20:02.944] [ALB] HTTP 200 OK returned to client in 842ms</text>''' if stage >= 7 else ''}
    {f'''<text x="14" y="118" fill="#94a3b8" font-size="7" font-family="monospace">[14:20:02.950] [MONITOR] Latency budget verified: DNS 14ms | LLM 410ms | DB 38ms</text>''' if stage >= 8 else ''}
    {f'''<text x="14" y="132" fill="#34d399" font-size="7" font-family="monospace">● Active Connection Pool: 8 connections &bull; 0 dropouts &bull; 0 err</text>''' if stage >= 8 else ''}
    {f'''<text x="14" y="146" fill="#f59e0b" font-size="7" font-family="monospace">✓ Egress SSL payload delivered securely via ACM TLS 1.3</text>''' if stage >= 8 else ''}
  </g>

  <!-- ==================== BOTTOM STATUS BAR ==================== -->
  <rect x="0" y="694" width="{WIDTH}" height="46" fill="#0b101c" stroke="#1e293b" stroke-width="1"/>
  
  <!-- Pill Indicator -->
  <rect x="18" y="704" width="165" height="26" rx="13" fill="{pill_color}"/>
  <text x="100" y="721" fill="#ffffff" font-size="9.5" font-weight="900" text-anchor="middle">{pill_label}</text>

  <!-- Narrative text -->
  <text x="195" y="721" fill="#f1f5f9" font-size="11.5" font-weight="600">{status_desc}</text>
  
  <text x="{WIDTH - 18}" y="721" fill="#64748b" font-size="9.5" font-family="monospace" text-anchor="end">Production Fargate v1.4.0 &bull; Python 3.11 &bull; LangGraph 0.2</text>
</svg>
"""
    return svg

def interp(p1, p2, t):
    """Linear interpolation between two 2D points."""
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

def build_pro_gif():
    frames = []
    durations = []

    def add_frame(stage, pos=None, color="#00f0ff", trails=None, step=1, dur=160):
        svg_code = make_pro_frame_svg(stage=stage, packet_pos=pos, packet_color=color, trail_positions=trails, step_index=step)
        doc = fitz.open(stream=svg_code.encode("utf-8"), filetype="svg")
        # 1.25x scaling for crisp, professional anti-aliased presentation display
        pix = doc[0].get_pixmap(dpi=120)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        frames.append(img)
        durations.append(dur)

    print("🎥 Rendering Stage 0: Client Initiation...")
    # Stage 0: User types and hits Send (packet at Client right edge)
    p_client_edge = (98, 245)
    for _ in range(3):
        add_frame(stage=0, pos=p_client_edge, color="#00f0ff", step=1, dur=280)

    print("🎥 Rendering Stage 1: Client -> Route 53...")
    # Stage 1: Packet moves from Client (98, 245) to Route 53 left edge (140, 245)
    p_r53_in = (140, 245)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_client_edge, p_r53_in, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=1, pos=pos, color="#00f0ff", trails=list(trail), step=2, dur=140)

    print("🎥 Rendering Stage 2: Route 53 -> ALB...")
    # Stage 2: Packet moves from Route 53 right edge (215, 245) to ALB left edge (255, 245)
    p_r53_out = (215, 245)
    p_alb_in = (255, 245)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_r53_out, p_alb_in, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=2, pos=pos, color="#00f0ff", trails=list(trail), step=2, dur=140)

    print("🎥 Rendering Stage 3: ALB Rule Match & Routing to Backend...")
    # Stage 3: ALB matches rule /chat* and forwards from ALB (345, 255) to Backend (385, 315)
    add_frame(stage=2, pos=p_alb_in, color="#c084fc", step=3, dur=260)
    p_alb_out = (345, 255)
    p_be_in = (385, 315)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_alb_out, p_be_in, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=3, pos=pos, color="#c084fc", trails=list(trail), step=3, dur=140)

    print("🎥 Rendering Stage 4: Backend Task 1 & SenseNova LLM...")
    # Stage 4: Inside Backend container, then packet travels to SenseNova LLM (715, 195)
    add_frame(stage=3, pos=(495, 315), color="#c084fc", step=4, dur=220)
    p_be_out_llm = (610, 295)
    p_llm_in = (715, 195)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_be_out_llm, p_llm_in, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=4, pos=pos, color="#f43f5e", trails=list(trail), step=5, dur=130)

    # SenseNova processes and returns
    add_frame(stage=4, pos=(797, 195), color="#f43f5e", step=5, dur=320)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_llm_in, p_be_out_llm, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=4, pos=pos, color="#f43f5e", trails=list(trail), step=5, dur=130)

    print("🎥 Rendering Stage 5: Backend -> Aiven MySQL...")
    # Stage 5: Backend executes SQL against Aiven MySQL (715, 325)
    p_be_out_mysql = (610, 325)
    p_mysql_in = (715, 325)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_be_out_mysql, p_mysql_in, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=5, pos=pos, color="#10b981", trails=list(trail), step=6, dur=130)

    # MySQL executes
    add_frame(stage=5, pos=(797, 325), color="#10b981", step=6, dur=300)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_mysql_in, p_be_out_mysql, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=5, pos=pos, color="#10b981", trails=list(trail), step=6, dur=130)

    print("🎥 Rendering Stage 6: Backend -> Supabase Postgres...")
    # Stage 6: Backend commits checkpoint to Supabase Postgres (715, 455)
    p_be_out_supa = (610, 355)
    p_supa_in = (715, 455)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_be_out_supa, p_supa_in, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=6, pos=pos, color="#06b6d4", trails=list(trail), step=7, dur=130)

    add_frame(stage=6, pos=(797, 455), color="#06b6d4", step=7, dur=260)
    trail = []
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interp(p_supa_in, p_be_out_supa, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=6, pos=pos, color="#06b6d4", trails=list(trail), step=7, dur=130)

    print("🎥 Rendering Stage 7: Response Return -> Client...")
    # Stage 7: Return packet travels Backend -> ALB -> Route 53 -> Client
    trail = []
    for i in range(5):
        t = (i + 1) / 5.0
        pos = interp(p_be_in, p_client_edge, t)
        trail.append(pos)
        if len(trail) > 3: trail.pop(0)
        add_frame(stage=7, pos=pos, color="#10b981", trails=list(trail), step=8, dur=130)

    print("🎥 Rendering Stage 8: Completed Response View (Hold)...")
    # Stage 8: Client renders STELLA AI response with product card and full telemetry
    # Hold for ~3.2 seconds so viewers can comfortably read all numbers and cards
    for _ in range(8):
        add_frame(stage=8, pos=None, color="#10b981", step=8, dur=400)

    return frames, durations

def main():
    assets_dir = Path("docs/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    gif_path = assets_dir / "architecture_chat_flow.gif"

    print("🚀 Compiling professional multi-stage SVG frames...")
    frames, durations = build_pro_gif()
    print(f"✅ Generated {len(frames)} frames. Optimizing adaptive color palette...")

    quantized = []
    for f in frames:
        q = f.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        quantized.append(q)

    quantized[0].save(
        str(gif_path),
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    size_mb = gif_path.stat().st_size / (1024 * 1024)
    print(f"🎉 Executive-grade GIF compiled: {gif_path} ({size_mb:.2f} MB, {len(frames)} frames)")

if __name__ == "__main__":
    main()
