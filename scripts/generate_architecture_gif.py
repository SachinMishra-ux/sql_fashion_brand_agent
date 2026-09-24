#!/usr/bin/env python3
"""
scripts/generate_architecture_gif.py
Generates a high-quality, animated GIF demonstrating the live network & data flow
when hitting the POST /chat endpoint in the Maison Luxé (STELLA) AWS architecture.
"""

from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

WIDTH = 1180
HEIGHT = 650

def make_frame_svg(stage: int, packet_pos=None, packet_color="#38bdf8", sub_progress: float = 0.0) -> str:
    """
    Renders an SVG string for a specific frame in the POST /chat sequence.
    stage:
      0: Initial idle / user clicks POST /chat
      1: Packet moving from Client -> Route 53
      2: Packet moving from Route 53 -> ALB
      3: ALB evaluates rule /chat* -> tg-fashion-backend
      4: Packet moving from ALB -> Backend Task 1
      5: Backend container processing, CPU rises
      6: Packet moving Backend -> SenseNova LLM
      7: SenseNova synthesizing SQL & returning
      8: Packet moving Backend -> Aiven MySQL
      9: Aiven MySQL executing SQL & returning 3 rows
      10: Packet moving Backend -> Supabase Postgres
      11: Supabase committing checkpoint & returning
      12: Response returning Backend -> ALB -> Client
      13: Completed! Response rendered in phone simulator, telemetry updated
    """
    # Active styling flags
    client_glow = (stage in [0, 1, 12, 13])
    dns_glow = (stage in [1, 2])
    alb_glow = (stage in [2, 3, 4, 12])
    alb_rule_be = (stage >= 3 and stage <= 12)
    be_glow = (stage in [4, 5, 6, 7, 8, 9, 10, 11, 12])
    llm_glow = (stage in [6, 7])
    mysql_glow = (stage in [8, 9])
    supabase_glow = (stage in [10, 11])
    
    # Paths styling
    wire_client_dns = "#38bdf8" if stage in [1, 2] else "#253349"
    wire_dns_alb = "#38bdf8" if stage in [2, 3] else "#253349"
    wire_alb_be = "#c084fc" if stage in [4, 5, 12] else "#253349"
    wire_be_llm = "#ec4899" if stage in [6, 7] else "#253349"
    wire_be_mysql = "#10b981" if stage in [8, 9] else "#253349"
    wire_be_supa = "#2dd4bf" if stage in [10, 11] else "#253349"

    # CPU bar
    if stage in [5, 6, 7, 8, 9, 10]:
        cpu_width = 46
        cpu_val = "36%"
        cpu_color = "#f59e0b"
    else:
        cpu_width = 24
        cpu_val = "20%"
        cpu_color = "#10b981"

    # Status pill and text
    if stage <= 1:
        pill_text = "CLIENT REQ"
        pill_bg = "#0284c7"
        status_text = "User sends POST /chat: &quot;Looking for a red silk evening gown under ₹20,000&quot;"
    elif stage == 2:
        pill_text = "DNS + SSL"
        pill_bg = "#0284c7"
        status_text = "Route 53 resolves predictoraa.com &bull; ACM TLS 1.3 Handshake completed"
    elif stage == 3:
        pill_text = "ALB ROUTING"
        pill_bg = "#8b5cf6"
        status_text = "ALB matches path &quot;/chat&quot; &rarr; Target Group: tg-fashion-backend (Port 8000)"
    elif stage in [4, 5]:
        pill_text = "ECS BACKEND"
        pill_bg = "#7e22ce"
        status_text = "FastAPI + LangGraph container activated in private subnet (AZ us-east-1a)"
    elif stage in [6, 7]:
        pill_text = "LLM INFERENCE"
        pill_bg = "#be185d"
        status_text = "SenseNova LLM parsing styling intent & synthesizing parameterized SQL query"
    elif stage in [8, 9]:
        pill_text = "SQL DATABASE"
        pill_bg = "#047857"
        status_text = "Executing SQL against Aiven Cloud MySQL: SELECT * FROM products WHERE price &lt;= 20000"
    elif stage in [10, 11]:
        pill_text = "SESSION MEMORY"
        pill_bg = "#0f766e"
        status_text = "Persisting conversation turn to Supabase PostgreSQL checkpointer (thread_id: usr_01)"
    elif stage == 12:
        pill_text = "RESPONSE RETURN"
        pill_bg = "#0284c7"
        status_text = "Returning synthesized AI styling recommendation JSON back through ALB to Client"
    else:
        pill_text = "COMPLETED 200 OK"
        pill_bg = "#10b981"
        status_text = "STELLA AI styling response &amp; live inventory card rendered on client (842ms)"

    # Telemetry HUD values
    latency_val = "842 ms" if stage >= 12 else ("310 ms" if stage >= 6 else "48 ms")
    latency_color = "#10b981" if stage >= 12 else "#38bdf8"
    http_status = "200 OK" if stage >= 12 else ("PROCESSING" if stage >= 3 else "IDLE")
    status_color = "#10b981" if stage >= 12 else ("#f59e0b" if stage >= 3 else "#94a3b8")

    # Simulator chat content
    user_bubble_visible = (stage >= 1)
    ai_typing_visible = (stage >= 3 and stage < 12)
    ai_response_visible = (stage >= 12)

    # SVG generation
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" style="background:#0a0e17; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <defs>
    <!-- Gradients & Filters -->
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#1f293d"/>
    </linearGradient>

    <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#38bdf8" flood-opacity="0.8"/>
    </filter>
    <filter id="glow-purple" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#c084fc" flood-opacity="0.8"/>
    </filter>
    <filter id="glow-green" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#10b981" flood-opacity="0.8"/>
    </filter>
    <filter id="glow-pink" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#ec4899" flood-opacity="0.8"/>
    </filter>
  </defs>

  <!-- TOP HEADER -->
  <rect x="0" y="0" width="{WIDTH}" height="56" fill="url(#headerGrad)" stroke="#1f2937" stroke-width="1"/>
  
  <!-- Logo Icon -->
  <rect x="18" y="10" width="36" height="36" rx="8" fill="#d97706"/>
  <text x="36" y="34" fill="#ffffff" font-size="18" font-weight="900" text-anchor="middle">S</text>

  <!-- Title & Subtitle -->
  <text x="66" y="27" fill="#ffffff" font-size="15" font-weight="700">STELLA AI Fashion Brand Agent <tspan fill="#94a3b8" font-size="12" font-weight="normal">| AWS Production Flow: POST /chat</tspan></text>
  <text x="66" y="44" fill="#64748b" font-size="10.5" font-family="monospace">Route 53 &bull; ALB (Path-Based Routing) &bull; ECS Fargate &bull; SenseNova LLM &bull; Aiven MySQL &bull; Supabase</text>

  <!-- Live Domain Pill -->
  <rect x="980" y="14" width="180" height="28" rx="14" fill="#064e3b" stroke="#10b981" stroke-width="1"/>
  <circle cx="996" cy="28" r="4.5" fill="#34d399"/>
  <text x="1008" y="32" fill="#34d399" font-size="10.5" font-family="monospace" font-weight="700">LIVE: predictoraa.com</text>

  <!-- CONTROLS SUB-HEADER -->
  <rect x="0" y="56" width="{WIDTH}" height="38" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
  <text x="18" y="79" fill="#94a3b8" font-size="10.5" font-weight="700">ACTIVE FLOW:</text>
  
  <!-- Inactive GET Button -->
  <rect x="110" y="62" width="135" height="25" rx="5" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="177" y="78" fill="#94a3b8" font-size="10" font-weight="600" text-anchor="middle">🌐 Browse UI (GET /)</text>

  <!-- Active POST /chat Button -->
  <rect x="255" y="62" width="220" height="25" rx="5" fill="#2563eb" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="365" y="78" fill="#ffffff" font-size="10" font-weight="700" text-anchor="middle">💬 AI Chat: Evening Gowns (POST /chat)</text>

  <!-- Clear History Button -->
  <rect x="485" y="62" width="170" height="25" rx="5" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="570" y="78" fill="#94a3b8" font-size="10" font-weight="600" text-anchor="middle">🗑️ Clear Chat (DELETE /chat)</text>

  <!-- Stress Test Button -->
  <rect x="665" y="62" width="125" height="25" rx="5" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="727" y="78" fill="#94a3b8" font-size="10" font-weight="600" text-anchor="middle">⚡ Stress Test</text>

  <!-- ==================== MAIN ARCHITECTURE CANVAS (LEFT) ==================== -->
  
  <!-- VPC Outer Box -->
  <rect x="235" y="105" width="575" height="495" rx="12" fill="#090d16" stroke="#334155" stroke-dasharray="4 4" stroke-width="1"/>
  <text x="250" y="124" fill="#64748b" font-size="10" font-family="monospace" font-weight="700">AWS VPC (10.0.0.0/16) - us-east-1</text>

  <!-- ECS Cluster Box -->
  <rect x="400" y="140" width="225" height="435" rx="10" fill="#0d1424" stroke="#f59e0b" stroke-dasharray="5 3" stroke-width="1.2"/>
  <text x="415" y="160" fill="#f59e0b" font-size="10" font-weight="700">AWS ECS Cluster (fashion-agent-cluster)</text>
  <text x="415" y="173" fill="#64748b" font-size="8.5" font-family="monospace">AWS Fargate Serverless</text>

  <!-- WIRE PATHS -->
  <!-- 1. Client to Route 53 -->
  <path d="M 85 240 L 130 240" fill="none" stroke="{wire_client_dns}" stroke-width="3" stroke-linecap="round"/>
  
  <!-- 2. Route 53 to ALB -->
  <path d="M 195 240 L 255 240" fill="none" stroke="{wire_dns_alb}" stroke-width="3" stroke-linecap="round"/>

  <!-- 3A. ALB to Frontend (inactive during POST /chat) -->
  <path d="M 335 225 C 365 225, 375 205, 415 205" fill="none" stroke="#1f293d" stroke-width="2"/>

  <!-- 3B. ALB to Backend (ACTIVE) -->
  <path d="M 335 255 C 365 255, 380 320, 415 320" fill="none" stroke="{wire_alb_be}" stroke-width="3" stroke-linecap="round"/>

  <!-- 4A. Backend to SenseNova LLM -->
  <path d="M 610 300 C 655 300, 675 185, 695 185" fill="none" stroke="{wire_be_llm}" stroke-width="2.8" stroke-linecap="round"/>

  <!-- 4B. Backend to Aiven MySQL -->
  <path d="M 610 325 C 655 325, 675 315, 695 315" fill="none" stroke="{wire_be_mysql}" stroke-width="2.8" stroke-linecap="round"/>

  <!-- 4C. Backend to Supabase Postgres -->
  <path d="M 610 350 C 655 350, 675 440, 695 440" fill="none" stroke="{wire_be_supa}" stroke-width="2.8" stroke-linecap="round"/>

  <!-- ==================== ARCHITECTURE NODES ==================== -->

  <!-- 1. Client Node -->
  <g transform="translate(18, 195)" {"filter='url(#glow-cyan)'" if client_glow else ""}>
    <rect width="68" height="90" rx="8" fill="#131d2e" stroke="{'#38bdf8' if client_glow else '#334155'}" stroke-width="{'2' if client_glow else '1'}"/>
    <rect width="68" height="20" rx="7" fill="#0284c7"/>
    <text x="34" y="14" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">CLIENT</text>
    <text x="34" y="38" fill="#f8fafc" font-size="9" font-weight="600" text-anchor="middle">Browser</text>
    <text x="34" y="52" fill="#94a3b8" font-size="7.5" font-family="monospace" text-anchor="middle">predictoraa</text>
    <text x="34" y="65" fill="#38bdf8" font-size="7" font-weight="600" text-anchor="middle">HTTPS 443</text>
    <text x="34" y="78" fill="#{'#34d399' if client_glow else '#64748b'}" font-size="7" font-weight="700" text-anchor="middle">● POST</text>
  </g>

  <!-- 2. Route 53 + ACM Node -->
  <g transform="translate(130, 195)" {"filter='url(#glow-cyan)'" if dns_glow else ""}>
    <rect width="65" height="90" rx="8" fill="#131d2e" stroke="{'#38bdf8' if dns_glow else '#334155'}" stroke-width="{'2' if dns_glow else '1'}"/>
    <rect width="65" height="20" rx="7" fill="#1e293b"/>
    <text x="32" y="14" fill="#38bdf8" font-size="7.5" font-weight="700" text-anchor="middle">ROUTE 53</text>
    <text x="32" y="38" fill="#f8fafc" font-size="8.5" font-weight="600" text-anchor="middle">DNS Alias</text>
    <text x="32" y="52" fill="#94a3b8" font-size="7" font-family="monospace" text-anchor="middle">ACM SSL</text>
    <text x="32" y="66" fill="#10b981" font-size="7" font-weight="600" text-anchor="middle">TLS 1.3 OK</text>
    <text x="32" y="78" fill="#64748b" font-size="6.5" text-anchor="middle">*.predictoraa</text>
  </g>

  <!-- 3. ALB Node -->
  <g transform="translate(245, 180)" {"filter='url(#glow-cyan)'" if alb_glow else ""}>
    <rect width="90" height="120" rx="8" fill="#131d2e" stroke="{'#38bdf8' if alb_glow else '#334155'}" stroke-width="{'2' if alb_glow else '1'}"/>
    <rect width="90" height="20" rx="7" fill="#0284c7"/>
    <text x="45" y="14" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">AWS ALB</text>
    <text x="45" y="36" fill="#f8fafc" font-size="8.5" font-weight="700" text-anchor="middle">alb-fashion</text>
    
    <!-- Rule Box 1: Frontend Default -->
    <rect x="5" y="44" width="80" height="18" rx="3" fill="#090d16" stroke="#1e293b"/>
    <text x="8" y="56" fill="#64748b" font-size="7" font-family="monospace">/* &rarr; TG:FE (80)</text>

    <!-- Rule Box 2: Backend Chat (HIGHLIGHTED) -->
    <rect x="5" y="66" width="80" height="22" rx="3" fill="{'#2e1065' if alb_rule_be else '#090d16'}" stroke="{'#c084fc' if alb_rule_be else '#1e293b'}" stroke-width="{'1.5' if alb_rule_be else '1'}"/>
    <text x="8" y="80" fill="{'#e9d5ff' if alb_rule_be else '#94a3b8'}" font-size="7" font-family="monospace" font-weight="700">/chat* &rarr; BE:8000</text>

    <text x="45" y="105" fill="#10b981" font-size="7" font-weight="600" text-anchor="middle">✓ Dual-AZ OK</text>
  </g>

  <!-- 4A. Frontend Task (Nginx) -->
  <g transform="translate(415, 175)">
    <rect width="195" height="60" rx="6" fill="#111827" stroke="#334155" stroke-width="1"/>
    <rect width="195" height="16" rx="5" fill="#0369a1"/>
    <text x="97" y="12" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle">fashion-frontend-service</text>
    <text x="10" y="31" fill="#38bdf8" font-size="8" font-weight="600">Container: Nginx (Alpine) :80</text>
    <text x="10" y="44" fill="#64748b" font-size="7.5">Serves: Luxury Catalog Static UI</text>
    <text x="10" y="54" fill="#10b981" font-size="7">Avg Latency: 12ms</text>
  </g>

  <!-- 4B. Backend Task 1 (FastAPI + LangGraph) ACTIVE -->
  <g transform="translate(415, 260)" {"filter='url(#glow-purple)'" if be_glow else ""}>
    <rect width="195" height="95" rx="6" fill="#16122a" stroke="{'#c084fc' if be_glow else '#334155'}" stroke-width="{'2' if be_glow else '1'}"/>
    <rect width="195" height="18" rx="5" fill="#7e22ce"/>
    <text x="97" y="13" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">fashion-backend-service (Task 1)</text>
    <text x="10" y="34" fill="#c084fc" font-size="8.5" font-weight="700">FastAPI + LangGraph (:8000)</text>
    <text x="10" y="47" fill="#cbd5e1" font-size="7.5">SQL Agent &bull; Intent Router &bull; Memory</text>
    
    <!-- CPU Meter -->
    <rect x="10" y="55" width="110" height="7" rx="3.5" fill="#1e293b"/>
    <rect x="10" y="55" width="{cpu_width}" height="7" rx="3.5" fill="{cpu_color}"/>
    <text x="126" y="62" fill="#94a3b8" font-size="7.5" font-family="monospace">CPU: {cpu_val}</text>
    <text x="10" y="77" fill="#10b981" font-size="7.5" font-weight="600">Health: Healthy (HTTP 200)</text>
    <text x="10" y="88" fill="#38bdf8" font-size="7" font-family="monospace">Private Subnet: 10.0.1.42</text>
  </g>

  <!-- 4C. Backend Task 2 (Auto-Scaling Replica - Standby) -->
  <g transform="translate(415, 380)" opacity="0.4">
    <rect width="195" height="65" rx="6" fill="#111827" stroke="#475569" stroke-dasharray="3 3" stroke-width="1"/>
    <rect width="195" height="16" rx="5" fill="#4c1d95"/>
    <text x="97" y="12" fill="#e9d5ff" font-size="8" font-weight="700" text-anchor="middle">fashion-backend-service (Task 2)</text>
    <text x="10" y="32" fill="#94a3b8" font-size="8">Replica: Auto-Scaling Standby</text>
    <text x="10" y="45" fill="#64748b" font-size="7.5">Target Tracking: CPU &gt; 70%</text>
    <text x="10" y="56" fill="#64748b" font-size="7">DesiredCount: 1 (Min: 1, Max: 3)</text>
  </g>

  <!-- 5A. SenseNova LLM Node -->
  <g transform="translate(695, 150)" {"filter='url(#glow-pink)'" if llm_glow else ""}>
    <rect width="110" height="70" rx="8" fill="#1f1122" stroke="{'#ec4899' if llm_glow else '#334155'}" stroke-width="{'2' if llm_glow else '1'}"/>
    <rect width="110" height="18" rx="7" fill="#be185d"/>
    <text x="55" y="13" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle">SenseNova LLM</text>
    <text x="8" y="33" fill="#f472b6" font-size="8" font-weight="700">SenseChat-5</text>
    <text x="8" y="45" fill="#94a3b8" font-size="7" font-family="monospace">HTTPS External</text>
    <text x="8" y="56" fill="#cbd5e1" font-size="7">Intent + SQL Gen</text>
    <text x="8" y="65" fill="#10b981" font-size="6.5">Latency: 410ms</text>
  </g>

  <!-- 5B. Aiven MySQL Node -->
  <g transform="translate(695, 280)" {"filter='url(#glow-green)'" if mysql_glow else ""}>
    <rect width="110" height="75" rx="8" fill="#0d231a" stroke="{'#10b981' if mysql_glow else '#334155'}" stroke-width="{'2' if mysql_glow else '1'}"/>
    <rect width="110" height="18" rx="7" fill="#047857"/>
    <text x="55" y="13" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle">Aiven Cloud MySQL</text>
    <text x="8" y="33" fill="#34d399" font-size="8" font-weight="700">Catalog &amp; Inventory</text>
    <text x="8" y="45" fill="#94a3b8" font-size="7" font-family="monospace">Port 16512 (TLS)</text>
    <text x="8" y="56" fill="#cbd5e1" font-size="7">Stock, Sizes, Prices</text>
    <text x="8" y="67" fill="#10b981" font-size="6.5">SQL Query: 38ms</text>
  </g>

  <!-- 5C. Supabase Postgres Node -->
  <g transform="translate(695, 405)" {"filter='url(#glow-green)'" if supabase_glow else ""}>
    <rect width="110" height="75" rx="8" fill="#0c1f20" stroke="{'#2dd4bf' if supabase_glow else '#334155'}" stroke-width="{'2' if supabase_glow else '1'}"/>
    <rect width="110" height="18" rx="7" fill="#0f766e"/>
    <text x="55" y="13" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle">Supabase Postgres</text>
    <text x="8" y="33" fill="#2dd4bf" font-size="8" font-weight="700">Memory Checkpoint</text>
    <text x="8" y="45" fill="#94a3b8" font-size="7" font-family="monospace">Port 5432 (Pooler)</text>
    <text x="8" y="56" fill="#cbd5e1" font-size="7">Multi-Turn History</text>
    <text x="8" y="67" fill="#38bdf8" font-size="6.5">Thread: usr_fashion_01</text>
  </g>

  <!-- MOVING PACKET DOT -->
  {f'<circle cx="{packet_pos[0]}" cy="{packet_pos[1]}" r="6.5" fill="{packet_color}" filter="url(#glow-cyan)"/>' if packet_pos else ''}

  <!-- ==================== RIGHT SIDE PANEL (SIMULATOR + LOGS) ==================== -->
  
  <!-- Right Container Border -->
  <rect x="825" y="105" width="340" height="495" rx="10" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>

  <!-- Telemetry HUD Bar (Top of Right Panel) -->
  <rect x="835" y="115" width="155" height="44" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="845" y="130" fill="#94a3b8" font-size="8" font-weight="700">ALB RESPONSE LATENCY</text>
  <text x="845" y="148" fill="{latency_color}" font-size="14" font-weight="800" font-family="monospace">{latency_val}</text>

  <rect x="1000" y="115" width="155" height="44" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="1010" y="130" fill="#94a3b8" font-size="8" font-weight="700">HTTP STATUS</text>
  <text x="1010" y="148" fill="{status_color}" font-size="14" font-weight="800" font-family="monospace">{http_status}</text>

  <!-- Smartphone Mockup Frame -->
  <rect x="835" y="168" width="320" height="280" rx="12" fill="#0b0f17" stroke="#334155" stroke-width="1.2"/>
  
  <!-- Phone Header -->
  <rect x="835" y="168" width="320" height="26" rx="11" fill="#1e293b"/>
  <circle cx="848" cy="181" r="3.5" fill="#10b981"/>
  <text x="858" y="184" fill="#ffffff" font-size="9" font-weight="700">STELLA Luxury Boutique</text>
  <text x="1140" y="184" fill="#94a3b8" font-size="8" font-family="monospace" text-anchor="end">🔒 predictoraa.com</text>

  <!-- Initial Greeting Bubble -->
  <rect x="845" y="202" width="220" height="28" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="853" y="215" fill="#e2e8f0" font-size="8.5" font-weight="700">STELLA AI:</text>
  <text x="853" y="225" fill="#94a3b8" font-size="8">Welcome to Maison Luxé! How may I assist you?</text>

  <!-- User Query Bubble -->
  {f'''
  <g>
    <rect x="915" y="238" width="230" height="34" rx="8" fill="#0284c7"/>
    <text x="923" y="252" fill="#ffffff" font-size="8" font-weight="700">You (Priya Sharma - VIP Platinum):</text>
    <text x="923" y="264" fill="#f0f9ff" font-size="8">Looking for a red silk evening gown under ₹20,000</text>
  </g>
  ''' if user_bubble_visible else ''}

  <!-- AI Typing Indicator -->
  {f'''
  <g>
    <rect x="845" y="280" width="160" height="22" rx="7" fill="#1e293b" stroke="#a855f7" stroke-width="1"/>
    <circle cx="860" cy="291" r="2.5" fill="#c084fc"/>
    <circle cx="868" cy="291" r="2.5" fill="#c084fc"/>
    <circle cx="876" cy="291" r="2.5" fill="#c084fc"/>
    <text x="888" y="294" fill="#c084fc" font-size="8" font-weight="600">STELLA reasoning...</text>
  </g>
  ''' if ai_typing_visible else ''}

  <!-- Final AI Response & Product Card -->
  {f'''
  <g>
    <!-- AI Intro text -->
    <rect x="845" y="278" width="295" height="22" rx="6" fill="#1e293b"/>
    <text x="853" y="292" fill="#e2e8f0" font-size="8">I found this perfect silk gown in our live collection:</text>

    <!-- Product Card -->
    <rect x="845" y="305" width="295" height="88" rx="8" fill="#151e2e" stroke="#2563eb" stroke-width="1.2"/>
    
    <!-- Product Thumbnail Placeholder -->
    <rect x="853" y="313" width="55" height="72" rx="5" fill="#991b1b"/>
    <text x="880" y="353" fill="#fca5a5" font-size="8" font-weight="700" text-anchor="middle">👗 GOWN</text>

    <!-- Product Details -->
    <text x="918" y="327" fill="#f8fafc" font-size="9" font-weight="700">Ruby Red Silk Crêpe Gown</text>
    <text x="918" y="339" fill="#94a3b8" font-size="7.5">Hand-draped bodice &bull; Micro-pleated</text>
    <text x="918" y="352" fill="#38bdf8" font-size="8.5" font-weight="700">₹18,500 <tspan fill="#64748b" font-size="7.5" font-weight="normal">(MRP: ₹22,000)</tspan></text>
    
    <!-- VIP Platinum Discount Badge -->
    <rect x="918" y="358" width="135" height="15" rx="3" fill="#064e3b" stroke="#10b981"/>
    <text x="923" y="369" fill="#34d399" font-size="7" font-weight="700">VIP Platinum: 15% Off (-₹2,775)</text>
    
    <text x="918" y="385" fill="#10b981" font-size="7.5" font-weight="600">✓ In Stock: 4 units (Aiven MySQL)</text>
  </g>
  ''' if ai_response_visible else ''}

  <!-- Phone Input Bar -->
  <rect x="835" y="416" width="320" height="32" rx="8" fill="#131d2e" stroke="#1f293d"/>
  <text x="848" y="436" fill="#64748b" font-size="8.5">Ask STELLA styling question...</text>
  <rect x="1100" y="422" width="45" height="20" rx="4" fill="#0284c7"/>
  <text x="1122" y="435" fill="#ffffff" font-size="8" font-weight="700" text-anchor="middle">Send</text>

  <!-- Live Terminal Logs (Bottom of Right Panel) -->
  <rect x="835" y="456" width="320" height="135" rx="8" fill="#06090e" stroke="#1e293b"/>
  <text x="845" y="470" fill="#64748b" font-size="8" font-weight="700" font-family="monospace">ECS &amp; ALB LOG STREAM</text>
  
  <text x="845" y="486" fill="#38bdf8" font-size="7.5" font-family="monospace">[ALB] 443 HTTPS &rarr; rule 1 matched (/chat*)</text>
  <text x="845" y="499" fill="#c084fc" font-size="7.5" font-family="monospace">[BE] POST /chat &rarr; FastAPI LangGraph agent</text>
  {f'''<text x="845" y="512" fill="#f472b6" font-size="7.5" font-family="monospace">[LLM] SenseNova: SQL synthesized (410ms)</text>''' if stage >= 7 else ''}
  {f'''<text x="845" y="525" fill="#34d399" font-size="7.5" font-family="monospace">[DB] Aiven MySQL: 3 items found (38ms)</text>''' if stage >= 9 else ''}
  {f'''<text x="845" y="538" fill="#2dd4bf" font-size="7.5" font-family="monospace">[DB] Supabase: Thread state committed</text>''' if stage >= 11 else ''}
  {f'''<text x="845" y="551" fill="#10b981" font-size="7.5" font-family="monospace">[ALB] 200 OK returned to client (842ms)</text>''' if stage >= 12 else ''}

  <!-- ==================== BOTTOM EXPLAINER STATUS BAR ==================== -->
  <rect x="0" y="608" width="{WIDTH}" height="42" fill="#0e1626" stroke="#1e293b" stroke-width="1"/>
  
  <!-- Step Pill -->
  <rect x="18" y="617" width="130" height="24" rx="12" fill="{pill_bg}"/>
  <text x="83" y="633" fill="#ffffff" font-size="9.5" font-weight="800" text-anchor="middle">{pill_text}</text>

  <!-- Step Detailed Explanation -->
  <text x="160" y="633" fill="#e2e8f0" font-size="11" font-weight="500">{status_text}</text>
  
  <text x="{WIDTH - 18}" y="633" fill="#64748b" font-size="9" font-family="monospace" text-anchor="end">AWS ECS Fargate &bull; us-east-1</text>
</svg>
"""
    return svg

def interpolate(p1, p2, t):
    """Linear interpolation between two (x, y) coordinates."""
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

def generate_all_frames():
    """Generates the list of PIL Images representing the animated GIF sequence."""
    frames = []
    durations = []

    # Sequence keypoints
    # Stage 0: User Click
    for _ in range(3):
        svg_data = make_frame_svg(stage=0)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        frames.append(img)
        durations.append(250)

    # Stage 1: Client -> Route 53
    p_start = (85, 240)
    p_end = (130, 240)
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=1, packet_pos=pos, packet_color="#38bdf8", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(150)

    # Stage 2: Route 53 -> ALB
    p_start = (195, 240)
    p_end = (255, 240)
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=2, packet_pos=pos, packet_color="#38bdf8", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(150)

    # Stage 3: ALB evaluates rule /chat* -> tg-fashion-backend
    for _ in range(3):
        svg_data = make_frame_svg(stage=3, packet_pos=(280, 240), packet_color="#38bdf8")
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(250)

    # Stage 4: ALB -> Backend Task 1
    p_start = (335, 255)
    p_end = (415, 320)
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=4, packet_pos=pos, packet_color="#c084fc", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 5: Backend processing, CPU meter rises
    for _ in range(2):
        svg_data = make_frame_svg(stage=5, packet_pos=(450, 320), packet_color="#c084fc")
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(220)

    # Stage 6: Backend -> SenseNova LLM
    p_start = (610, 300)
    p_end = (695, 185)
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=6, packet_pos=pos, packet_color="#ec4899", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 7: SenseNova LLM returning
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_end, p_start, t)
        svg_data = make_frame_svg(stage=7, packet_pos=pos, packet_color="#ec4899", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 8: Backend -> Aiven MySQL
    p_start = (610, 325)
    p_end = (695, 315)
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=8, packet_pos=pos, packet_color="#10b981", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 9: Aiven MySQL returning
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_end, p_start, t)
        svg_data = make_frame_svg(stage=9, packet_pos=pos, packet_color="#10b981", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 10: Backend -> Supabase Postgres
    p_start = (610, 350)
    p_end = (695, 440)
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=10, packet_pos=pos, packet_color="#2dd4bf", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 11: Supabase Postgres returning
    for i in range(3):
        t = (i + 1) / 3.0
        pos = interpolate(p_end, p_start, t)
        svg_data = make_frame_svg(stage=11, packet_pos=pos, packet_color="#2dd4bf", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 12: Backend -> ALB -> Client
    p_start = (415, 320)
    p_end = (85, 240)
    for i in range(4):
        t = (i + 1) / 4.0
        pos = interpolate(p_start, p_end, t)
        svg_data = make_frame_svg(stage=12, packet_pos=pos, packet_color="#10b981", sub_progress=t)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(140)

    # Stage 13: Response completed & sustained view
    for _ in range(6):
        svg_data = make_frame_svg(stage=13)
        doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=96)
        frames.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        durations.append(400)  # Total hold ~2.4 seconds

    return frames, durations

def main():
    assets_dir = Path("docs/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    gif_path = assets_dir / "architecture_chat_flow.gif"

    print("🚀 Generating animation frames from vector SVG...")
    frames, durations = generate_all_frames()
    print(f"✅ Generated {len(frames)} frames. Optimizing and compiling GIF...")

    # Quantize frames to 256-color palette for crisp rendering & optimized size
    quantized_frames = []
    for f in frames:
        q_frame = f.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        quantized_frames.append(q_frame)

    quantized_frames[0].save(
        str(gif_path),
        save_all=True,
        append_images=quantized_frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    size_mb = gif_path.stat().st_size / (1024 * 1024)
    print(f"🎉 Animated GIF successfully generated: {gif_path} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
