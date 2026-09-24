# 🧪 Stress Testing & ECS Auto-Scaling Guide
### Complete Runbook for Load Testing with Postman & Configuring Fargate Auto-Scaling

---

## 📑 Table of Contents
1. [Overview & Objectives](#1-overview--objectives)
2. [How Auto-Scaling Works in AWS ECS Fargate](#2-how-auto-scaling-works-in-aws-ecs-fargate)
3. [Step-by-Step Auto-Scaling Configuration](#3-step-by-step-auto-scaling-configuration)
4. [Setting Up Postman Performance & Stress Testing](#4-setting-up-postman-performance--stress-testing)
5. [Automated Python Multi-Threaded Stress Test](#-5-alternative-automated-python-multi-threaded-stress-test)
6. [Live Monitoring During Stress Testing](#-6-live-monitoring-during-stress-testing)
7. [Verifying Scale-Up & Scale-Down in Real Time](#-7-verifying-scale-up--scale-down-in-real-time)
8. [Student Teaching Points & Summary](#-8-student-teaching-points--summary)

---

## 🎯 1. Overview & Objectives

In production web applications, user traffic fluctuates dramatically. A fixed single-container deployment will experience slow response times or server crashes when concurrent requests surge.

### Goals of this Guide:
1. **Enable AWS Application Auto Scaling** on `fashion-backend-service` to automatically scale from **1 task up to 5 tasks** when CPU utilization exceeds **70%**.
2. **Execute a Stress Test using Postman** simulating **10 to 100 concurrent Virtual Users (VUs)**.
3. **Monitor Live CloudWatch Metrics & Logs** to observe zero-downtime scaling and automatic scale-down after traffic subsides.

---

## ⚙️ 2. How Auto-Scaling Works in AWS ECS Fargate

AWS uses **Target Tracking Scaling Policies**, which act like a home thermostat: you set a target (e.g., 70% CPU), and AWS continuously adjusts the number of container tasks to keep the average utilization near that target.

```text
========================================================================================================================
                                      THE AUTO-SCALING LIFECYCLE
========================================================================================================================

  [ STATE 1: IDLE / LOW TRAFFIC ]
  • Desired Tasks: 1
  • CPU Utilization: ~5% - 15%
  • Cost: Minimum (~$0.01/hour)
                │
                │ (1) Postman launches 50 Virtual Users (Surge in HTTP Requests)
                ▼
  [ STATE 2: ALARM TRIGGERED ]
  • CPU Utilization crosses 70% for > 60 seconds
  • CloudWatch Alarm transitions to ALARM state
  • Application Auto Scaling requests +1 to +2 tasks from ECS
                │
                │ (2) Fargate provisions new MicroVMs
                ▼
  [ STATE 3: SCALE-OUT COMPLETE (HIGH LOAD) ]
  • Desired Tasks: 2 ──▶ 3 ──▶ 4 tasks running in parallel
  • ALB registers new container IPs automatically
  • Average CPU drops back down to ~50% - 65%
  • Zero dropped requests / low latency maintained
                │
                │ (3) Postman stress test finishes (Traffic drops back to 0)
                ▼
  [ STATE 4: COOLDOWN & SCALE-IN ]
  • CPU Utilization drops to < 10%
  • Scale-In Cooldown Timer (300 seconds / 5 minutes) ensures stability
  • ECS gracefully drains traffic and stops extra containers
  • Service returns to Desired Tasks: 1
```

---

## 🛠️ 3. Step-by-Step Auto-Scaling Configuration

You can enable auto-scaling using either the **AWS Console** or the **AWS CLI**.

### Option A: Via AWS Console (Recommended)

1. Open **AWS ECS Console** $\rightarrow$ Click **Clusters** $\rightarrow$ Open **`fashion-agent-cluster`**.
2. Under the **Services** tab, select **`fashion-backend-service`** $\rightarrow$ Click **Update** (top right).
3. Scroll down to the **Service auto scaling** section:
   - Check the box: **`Use service auto scaling`**.
   - **Minimum number of tasks**: `1` *(Ensures baseline cost is minimal)*.
   - **Maximum number of tasks**: `5` *(Safety ceiling to control AWS billing)*.
4. Under **Scaling policies** $\rightarrow$ Click **Add scaling policy**:
   - **Policy name**: `cpu-70-target-tracking`
   - **ECS service metric**: `ECSServiceAverageCPUUtilization`
   - **Target value**: `70`
   - **Scale-out cooldown period**: `60` seconds *(How fast to spin up new tasks)*.
   - **Scale-in cooldown period**: `300` seconds *(How long to wait before terminating tasks)*.
5. Click **Update** at the bottom of the page.

---

### Option B: Via AWS CLI (1-Click Terminal Setup)

Run these two commands in your local terminal:

```bash
# 1. Register the backend service as an Application Auto Scaling target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/fashion-agent-cluster/fashion-backend-service \
  --min-capacity 1 \
  --max-capacity 5 \
  --region ap-south-1

# 2. Attach the 70% CPU Target Tracking Scaling Policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/fashion-agent-cluster/fashion-backend-service \
  --policy-name "CPU-Target-70" \
  --policy-type "TargetTrackingScaling" \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }' \
  --region ap-south-1
```

---

## 📮 4. Setting Up Postman Performance & Stress Testing

### Step 4.1: Retrieve a Signed JWT Demo Token
Because the backend API is protected with JWT authentication, all `/chat` calls require a valid `Authorization: Bearer <token>` header:

1. Send a request to `GET https://predictoraa.com/auth/users`.
2. Copy the signed `token` for user **Priya Sharma** (Platinum tier).

---

### Step 4.2: Create the Postman Collection & Add Authentication
1. Open **Postman** $\rightarrow$ Click **Collections** (left menu) $\rightarrow$ Click **+** (New Collection).
2. Name the collection: **`Maison Luxe - Stress Test`**.
3. Set Collection-Level Authentication:
   - Click on the collection name $\rightarrow$ Open the **`Authorization`** tab.
   - **Type**: Select **`Bearer Token`**.
   - **Token**: Paste your JWT token.
   - Press **`Cmd + S`** (`Ctrl + S`) to save.

---

### Step 4.3: Add Test Endpoints to the Collection

#### Request 1: Fast Health Check (Lightweight Baseline)
* **Method**: `GET`
* **URL**: `https://predictoraa.com/health`

#### Request 2: Catalog Products (Database Read Heavy)
* **Method**: `GET`
* **URL**: `https://predictoraa.com/products`

#### Request 3: AI Stylist Chat (Agentic Reasoning Heavy)
* **Method**: `POST`
* **URL**: `https://predictoraa.com/chat`
* **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <YOUR_JWT_TOKEN>`
* **Body** (raw JSON):
  ```json
  {
    "message": "Recommend 3 luxury silk evening dresses under $600 with matching accessories",
    "session_id": "postman_load_user_01"
  }
  ```
* ⚠️ **CRITICAL POSTMAN STEP**: Click **`Save` (`Cmd + S`)** on each request! If a tab displays an **orange dot**, the changes are unsaved, and the Collection Runner will execute without the auth header (`401 Unauthorized`).

---

### Step 4.4: Launch the Postman Performance Runner

1. Click on the collection name **`Maison Luxe - Stress Test`** $\rightarrow$ Click the **Run** button (top right).
2. Switch from the *Functional* tab to the **`Performance`** tab.
3. Set test configuration:
   - **Virtual Users (VUs)**: Start with `5` to `10` for AI Chat (or `50` for `/health` and `/products`).
   - **Test Duration**: `2 to 3 minutes`.
   - **Load Profile**: Choose **Ramp up** (Starts at 2 users and climbs to 10 users over 45 seconds).
4. Click **Run**.
5. Observe the live Postman performance chart:
   - **Throughput (Requests/sec)**
   - **Response Time (Average & p90/p95/p99)**
   - **Error Rate (Should remain 0.00%)**

---

## 🐍 5. Alternative: Automated Python Multi-Threaded Stress Test

For automated, scriptable load testing directly from the terminal without GUI caching issues, run the included script:

```bash
# Run with 5 concurrent users (loads token automatically from .env or live auth)
python3 scripts/stress_test.py --users 5
```

You can optionally place your custom token or settings in a local `.env` file:
```bash
# Optional .env configuration
JWT_TOKEN="your_jwt_token_here"
CONCURRENT_USERS=5
CHAT_API_URL="https://predictoraa.com/chat"
```

The script ([scripts/stress_test.py](file:///Users/sachinmishra/Desktop/sql_fashion_brand_agent/scripts/stress_test.py)):
1. Checks for `JWT_TOKEN` in `.env`.
2. If not found, dynamically calls `GET https://predictoraa.com/auth/users` to fetch a fresh token for Priya Sharma.
3. Fires concurrent requests using Python's `threading` module and reports latency & success rates.

---

## 📊 6. Live Monitoring During Stress Testing

While Postman or Python is generating traffic, monitor the AWS infrastructure in real time:

### 1. CloudWatch Live Tail (Real-Time Request Logs)
* Go to **AWS Console** $\rightarrow$ **CloudWatch** $\rightarrow$ **Logs** $\rightarrow$ **Log Management** $\rightarrow$ **`/ecs/fashion-backend`**.
* Click **Start Live Tail** (or **Start tailing**) in the top right.
* Watch real-time incoming HTTP requests, SQL queries, and LangChain execution times stream past.

### 2. ECS Service CPU & Task Metrics
* Go to **ECS** $\rightarrow$ **Clusters** $\rightarrow$ **`fashion-agent-cluster`** $\rightarrow$ Click **`fashion-backend-service`**.
* Click the **Health and metrics** tab:
  - Watch **CPUUtilization** climb from 5% towards 80%+.
  - Watch **MemoryUtilization** stability.

### 3. Application Load Balancer Metrics
* Go to **EC2** $\rightarrow$ **Load Balancers** $\rightarrow$ Select **`alb-fashion-agent`** $\rightarrow$ **Monitoring** tab:
  - **Request Count**: Shows total requests per minute.
  - **Target Response Time**: Average latency in milliseconds.
  - **HTTP 2XX / 5XX**: Confirms zero server error responses.

---

## 🔍 7. Verifying Scale-Up & Scale-Down in Real Time

### How to verify Scale-Up:
1. In the **`fashion-backend-service`** page, open the **Events** tab.
2. When CPU exceeds 70% for 60 seconds, you will see events such as:
   ```text
   service fashion-backend-service has started 1 tasks: (task 8a1b2c...).
   service fashion-backend-service has reached a steady state with 2 tasks running.
   ```
3. Under the **Deployments and tasks** tab, you will see **`2/2 tasks running`** (or `3/3 tasks running`).
4. The Application Load Balancer target group (`tg-fashion-backend`) will automatically display 2+ **Healthy** target IPs.

### How to verify Scale-Down:
1. Once the stress test finishes, CPU utilization will drop below 10%.
2. After the **300-second cooldown period**, check the **Events** tab:
   ```text
   service fashion-backend-service has stopped 1 tasks: (task 8a1b2c...).
   service fashion-backend-service has reached a steady state with 1 tasks running.
   ```
3. The service safely returns to **`1/1 tasks running`**, saving infrastructure costs.

---

## 🎓 8. Student Teaching Points & Summary

| Concept | Explanation |
| :--- | :--- |
| **Why 70% CPU Threshold?** | 70% leaves a 30% safety headroom while new containers spin up (~30–45s) so existing users never experience dropped requests. |
| **Why a 300s Scale-In Cooldown?** | Prevents "flapping" (rapidly spinning up and shutting down containers if traffic is bursty/intermittent). |
| **Horizontal vs Vertical Scaling** | **Vertical** = Increasing CPU/RAM of 1 container (requires restart).<br/>**Horizontal** = Adding more parallel containers behind the Load Balancer (zero downtime). |
| **Cost Optimization** | With Fargate, you only pay per second for the extra containers during the spike. When idle, you only pay for 1 container. |
