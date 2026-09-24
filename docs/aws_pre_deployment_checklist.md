# 📋 AWS Account Pre-Deployment Checklist
### Everything You Need to Set Up in AWS Before Triggering the GitHub Actions CI/CD Pipeline

> **Target Domain:** `https://predictoraa.com` (and `https://www.predictoraa.com`)  
> **Estimated Setup Time:** ~25–35 minutes (one-time setup)  
> **Prerequisites:** AWS Account (Admin access) & GoDaddy Account

---

## 📑 Summary of 10 Setup Phases

| Phase | AWS Service | Purpose | Done? |
| :--- | :--- | :--- | :---: |
| **Phase 1** | **VPC & Security Groups** | Configure network isolation, ALB firewall, and container firewalls | [ ] |
| **Phase 2** | **Amazon ECR** | Create private Docker image registries for Frontend and Backend | [ ] |
| **Phase 3** | **SSM Parameter Store** | Store database passwords & SenseNova API keys securely | [ ] |
| **Phase 4** | **CloudWatch Logs** | Create log streams to monitor application errors & access | [ ] |
| **Phase 5** | **IAM Roles & User** | Set up Fargate execution role & GitHub Actions deployer user | [ ] |
| **Phase 6** | **Route 53 & GoDaddy** | Create DNS hosted zone and delegate GoDaddy nameservers | [ ] |
| **Phase 7** | **AWS ACM (SSL/TLS)** | Issue free wildcard HTTPS certificate for `predictoraa.com` | [ ] |
| **Phase 8** | **Application Load Balancer** | Create ALB, target groups, HTTPS listener & HTTP-to-HTTPS redirect | [ ] |
| **Phase 9** | **Route 53 DNS Mapping** | Point `predictoraa.com` and `www` directly to the ALB via Alias | [ ] |
| **Phase 10** | **ECS Cluster & Services** | Create the Fargate cluster & initial service placeholders | [ ] |
| **Phase 11** | **GitHub Secrets** | Add AWS credentials to your GitHub repository settings | [ ] |

---

## 🌍 Step 0: Choose Your AWS Region

Select the AWS region where you want all your resources deployed.
- **Recommended Regions:**
  - `ap-south-1` (Asia Pacific - Mumbai) — Lowest latency for India
  - `us-east-1` (US East - N. Virginia) — Most cost-effective, standard global region
- **Important:** Ensure you stay in this **same region** across all services (ECR, ECS, ALB, ACM, and SSM).

---

## 🛡️ Phase 1: Security Groups & Networking

You can use your AWS account's **Default VPC** (which already has an Internet Gateway and public subnets in each Availability Zone).

### 1.1 Create the ALB Security Group (`alb-sg`)
This security group controls public internet traffic into the Load Balancer.

1. Open AWS Console $\rightarrow$ Navigate to **VPC** $\rightarrow$ Click **Security Groups** $\rightarrow$ Click **Create security group**.
2. **Security group name**: `alb-sg`
3. **Description**: `Allow inbound HTTP and HTTPS from internet to ALB`
4. **VPC**: Select your default VPC.
5. **Inbound rules** (add 2 rules):
   - **Type**: `HTTP` | **Port**: `80` | **Source**: `Anywhere-IPv4` (`0.0.0.0/0`)
   - **Type**: `HTTPS` | **Port**: `443` | **Source**: `Anywhere-IPv4` (`0.0.0.0/0`)
6. **Outbound rules**: Leave default (`All traffic` to `0.0.0.0/0`).
7. Click **Create security group**. *(Note down the Security Group ID, e.g., `sg-0123alb...`)*.

---

### 1.2 Create the ECS Tasks Security Group (`ecs-tasks-sg`)
This security group protects your Fargate containers. Containers only accept traffic from the ALB.

1. In **Security Groups**, click **Create security group**.
2. **Security group name**: `ecs-tasks-sg`
3. **Description**: `Allow inbound traffic from ALB only`
4. **VPC**: Select your default VPC.
5. **Inbound rules** (add 2 rules):
   - **Type**: `Custom TCP` | **Port**: `80` (Frontend) | **Source**: Select `Custom` $\rightarrow$ choose `alb-sg`
   - **Type**: `Custom TCP` | **Port**: `8000` (Backend) | **Source**: Select `Custom` $\rightarrow$ choose `alb-sg`
6. **Outbound rules**:
   - **Type**: `All traffic` | **Destination**: `Anywhere-IPv4` (`0.0.0.0/0`)  
     *(Required so the backend container can reach Aiven MySQL on port 16512, Supabase PostgreSQL on port 5432, and SenseNova API over HTTPS).*
7. Click **Create security group**. *(Note down the Security Group ID, e.g., `sg-0456ecs...`)*.

---

## 📦 Phase 2: Create Amazon ECR Repositories

Create 2 private registries to store your Docker images:

1. In AWS Console $\rightarrow$ Search for **ECR** (Elastic Container Registry).
2. Click **Create repository**:
   - **Visibility**: `Private`
   - **Repository name**: `fashion-backend`
   - **Tag immutability**: Leave `Disabled` (or Enabled if preferred)
   - **Scan on push**: Toggle **Enabled** (scans for security vulnerabilities)
   - Click **Create repository**.
3. Click **Create repository** again:
   - **Visibility**: `Private`
   - **Repository name**: `fashion-frontend`
   - **Scan on push**: Toggle **Enabled**
   - Click **Create repository**.

> **AWS CLI Alternative:**
> ```bash
> aws ecr create-repository --repository-name fashion-backend --image-scanning-configuration scanOnPush=true
> aws ecr create-repository --repository-name fashion-frontend --image-scanning-configuration scanOnPush=true
> ```

---

## 🔐 Phase 3: Store Secrets in AWS SSM Parameter Store

Your database passwords and SenseNova API keys will be stored encrypted in AWS Systems Manager (SSM) so they are never stored in Git or inside Docker images.

1. In AWS Console $\rightarrow$ Search for **Systems Manager** $\rightarrow$ Click **Parameter Store** (in the left sidebar under *Application Management*).
2. Click **Create parameter** for each of the following:

| Name | Type | Value |
| :--- | :--- | :--- |
| `/fashion-agent/SENSENOVA_API_KEY` | **SecureString** | `YOUR_SENSENOVA_API_KEY` |
| `/fashion-agent/MYSQL_HOST` | **String** | `YOUR_AIVEN_MYSQL_HOST.aivencloud.com` |
| `/fashion-agent/MYSQL_PORT` | **String** | `16512` |
| `/fashion-agent/MYSQL_USER` | **String** | `avnadmin` |
| `/fashion-agent/MYSQL_PASSWORD` | **SecureString** | `YOUR_AIVEN_MYSQL_PASSWORD` |
| `/fashion-agent/MYSQL_DATABASE` | **String** | `defaultdb` |
| `/fashion-agent/POSTGRES_HOST` | **String** | `YOUR_SUPABASE_HOST.pooler.supabase.com` |
| `/fashion-agent/POSTGRES_PORT` | **String** | `5432` |
| `/fashion-agent/POSTGRES_USER` | **String** | `postgres.YOUR_PROJECT_REF` |
| `/fashion-agent/POSTGRES_PASSWORD` | **SecureString** | `YOUR_SUPABASE_PASSWORD` |
| `/fashion-agent/POSTGRES_DB` | **String** | `postgres` |
| `/fashion-agent/POSTGRES_CONN_STR` | **SecureString** | `postgresql://postgres.YOUR_PROJECT_REF:YOUR_SUPABASE_PASSWORD@YOUR_SUPABASE_HOST.pooler.supabase.com:5432/postgres` |

> **Fast 1-Click AWS CLI Commands (Run in terminal if you have AWS CLI configured):**
> ```bash
> aws ssm put-parameter --name "/fashion-agent/SENSENOVA_API_KEY" --value "YOUR_SENSENOVA_API_KEY" --type "SecureString" --overwrite
> aws ssm put-parameter --name "/fashion-agent/MYSQL_HOST" --value "YOUR_AIVEN_MYSQL_HOST.aivencloud.com" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/MYSQL_PORT" --value "16512" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/MYSQL_USER" --value "avnadmin" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/MYSQL_PASSWORD" --value "YOUR_AIVEN_MYSQL_PASSWORD" --type "SecureString" --overwrite
> aws ssm put-parameter --name "/fashion-agent/MYSQL_DATABASE" --value "defaultdb" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/POSTGRES_HOST" --value "YOUR_SUPABASE_HOST.pooler.supabase.com" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/POSTGRES_PORT" --value "5432" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/POSTGRES_USER" --value "postgres.YOUR_PROJECT_REF" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/POSTGRES_PASSWORD" --value "YOUR_SUPABASE_PASSWORD" --type "SecureString" --overwrite
> aws ssm put-parameter --name "/fashion-agent/POSTGRES_DB" --value "postgres" --type "String" --overwrite
> aws ssm put-parameter --name "/fashion-agent/POSTGRES_CONN_STR" --value "postgresql://postgres.YOUR_PROJECT_REF:YOUR_SUPABASE_PASSWORD@YOUR_SUPABASE_HOST.pooler.supabase.com:5432/postgres" --type "SecureString" --overwrite
> ```

---

## 🪵 Phase 4: Create CloudWatch Log Groups

1. In AWS Console $\rightarrow$ Search for **CloudWatch** $\rightarrow$ Click **Log Managament** (under *Logs* in left menu).
2. Click **Create log group**:
   - **Log group name**: `/ecs/fashion-backend`
   - **Retention**: `30 days` (or your choice)
   - Click **Create**.
3. Click **Create log group** again:
   - **Log group name**: `/ecs/fashion-frontend`
   - **Retention**: `30 days`
   - Click **Create**.

> **AWS CLI Alternative:**
> ```bash
> aws logs create-log-group --log-group-name "/ecs/fashion-backend" --region ap-south-1
> aws logs put-retention-policy --log-group-name "/ecs/fashion-backend" --retention-in-days 30 --region ap-south-1
> aws logs create-log-group --log-group-name "/ecs/fashion-frontend" --region ap-south-1
aws logs put-retention-policy --log-group-name "/ecs/fashion-frontend" --retention-in-days 30 --region ap-south-1
> ```

---

## 👤 Phase 5: IAM Roles & GitHub Actions User

### 5.1 Create the ECS Task Execution Role (`ecsTaskExecutionRole`)
This role allows Fargate tasks to download Docker images from ECR, decrypt SSM parameters, and stream logs to CloudWatch.

1. In AWS Console $\rightarrow$ Search for **IAM** $\rightarrow$ Click **Roles** $\rightarrow$ Click **Create role**.
2. **Trusted entity type**: Select **AWS service**.
3. **Use case**: Choose **Elastic Container Service** $\rightarrow$ Select **Elastic Container Service Task** $\rightarrow$ Click **Next**.
4. **Add permissions**:
   - Search for `AmazonECSTaskExecutionRolePolicy` $\rightarrow$ Check the box.
   - Click **Next**.
5. **Role name**: `ecsTaskExecutionRole`
6. Click **Create role**.
7. Now open the newly created `ecsTaskExecutionRole`:
   - Click **Add permissions** $\rightarrow$ **Create inline policy**.
   - Switch to **JSON** tab and paste:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": [
             "ssm:GetParameters",
             "ssm:GetParameter",
             "secretsmanager:GetSecretValue",
             "kms:Decrypt"
           ],
           "Resource": "*"
         }
       ]
     }
     ```
   - Click **Next** $\rightarrow$ Name it `ReadSSMAndSecrets` $\rightarrow$ Click **Create policy**.

---

### 5.2 Create the IAM User for GitHub Actions (`github-actions-deployer`)
This user gives GitHub Actions permission to push images to ECR and deploy to ECS.

1. In **IAM** $\rightarrow$ Click **Users** $\rightarrow$ Click **Create user**.
2. **User name**: `github-actions-deployer` $\rightarrow$ Click **Next**.
3. **Set permissions**: Select **Attach policies directly**.
4. Attach these AWS managed policies:
   - `AmazonEC2ContainerRegistryPowerUser` (to push Docker images to ECR)
   - `AmazonECS_FullAccess` (to update ECS task definitions and services)
5. Click **Next** $\rightarrow$ Click **Create user**.
6. Open the newly created `github-actions-deployer`:
   - Click **Security credentials** tab.
   - Scroll to **Access keys** $\rightarrow$ Click **Create access key**.
   - Select **Third-party service** $\rightarrow$ Click **Next** $\rightarrow$ Click **Create access key**.
   - **CRITICAL:** Copy the **Access Key ID** and **Secret Access Key** and save them safely. You will paste them into GitHub Repository Secrets in Phase 11.

---

## 🌐 Phase 6: Amazon Route 53 & GoDaddy Nameserver Delegation

### 6.1 Create Route 53 Public Hosted Zone
1. In AWS Console $\rightarrow$ Search for **Route 53** $\rightarrow$ Click **Hosted zones** $\rightarrow$ Click **Create hosted zone**.
2. **Domain name**: `predictoraa.com`
3. **Type**: **Public hosted zone**
4. Click **Create hosted zone**.
5. Inside the hosted zone, look at the record of type **NS (Name Server)**. It lists **4 nameservers**, for example:
   - `ns-123.awsdns-45.org`
   - `ns-678.awsdns-90.com`
   - `ns-112.awsdns-33.net`
   - `ns-445.awsdns-66.co.uk`
   *(Copy these 4 nameserver addresses)*.

---

### 6.2 Update Nameservers in GoDaddy
1. Log into your **GoDaddy Account** (https://www.godaddy.com).
2. Go to **My Products** $\rightarrow$ Click **Domains** $\rightarrow$ Click **predictoraa.com**.
3. Click **DNS** (or **Manage DNS**).
4. Scroll down to the **Nameservers** section.
5. Click **Change Nameservers** $\rightarrow$ Select **I'll use my own nameservers** (Advanced).
6. Paste the **4 AWS nameserver addresses** from Step 6.1 (without any trailing dots).
7. Click **Save** and confirm the prompt.
   > ⏳ *Note: DNS propagation between GoDaddy and AWS takes 5 to 30 minutes.*

---

## 🔒 Phase 7: Request Free SSL/TLS Certificate in AWS Certificate Manager (ACM)

1. In AWS Console $\rightarrow$ Search for **Certificate Manager** (ACM).
   *(Make sure you are in the same region as your VPC and ALB, e.g., `ap-south-1` or `us-east-1`)*.
2. Click **Request a certificate** $\rightarrow$ Choose **Request a public certificate** $\rightarrow$ Click **Next**.
3. **Domain names**:
   - Line 1: `predictoraa.com`
   - Line 2 (click *Add another name to this certificate*): `*.predictoraa.com`
4. **Validation method**: **DNS validation** (Recommended).
5. Click **Request**.
6. Open the newly requested certificate:
   - Click the button **Create records in Route 53**.
   - Click **Create records**.
   - ACM will automatically insert the validation CNAME records into your Route 53 hosted zone!
7. Within 2–5 minutes, refresh the page until the certificate status displays: **Issued ✅** in green.

---

## ⚖️ Phase 8: Application Load Balancer (ALB) & Target Groups

### 8.1 Create Target Group for Frontend (Port 80)
1. In AWS Console $\rightarrow$ Navigate to **EC2** $\rightarrow$ In the left menu scroll down to **Target Groups** $\rightarrow$ Click **Create target group**.
2. **Target type**: Choose **IP addresses**.
3. **Target group name**: `tg-fashion-frontend`
4. **Protocol**: `HTTP` | **Port**: `80`
5. **IP address type**: `IPv4`
6. **VPC**: Select your default VPC.
7. **Health checks**: Path: `/`
8. Click **Next** $\rightarrow$ Click **Create target group** *(do not register any IP manually, ECS will do this automatically)*.

---

### 8.2 Create Target Group for Backend (Port 8000)
1. Click **Create target group**.
2. **Target type**: Choose **IP addresses**.
3. **Target group name**: `tg-fashion-backend`
4. **Protocol**: `HTTP` | **Port**: `8000`
5. **VPC**: Select your default VPC.
6. **Health checks**:
   - **Health check path**: `/health`
   - Expand *Advanced health check settings*:
     - **Healthy threshold**: `2`
     - **Timeout**: `5 seconds`
     - **Interval**: `15 seconds`
7. Click **Next** $\rightarrow$ Click **Create target group**.

---

### 8.3 Create the Application Load Balancer
1. In EC2 left menu $\rightarrow$ Click **Load Balancers** $\rightarrow$ Click **Create load balancer**.
2. Under **Application Load Balancer**, click **Create**.
3. **Basic configuration**:
   - **Load balancer name**: `alb-fashion-agent`
   - **Scheme**: **Internet-facing**
   - **IP address type**: `IPv4`
4. **Network mapping**:
   - **VPC**: Select your default VPC.
   - **Mappings**: Check at least **2 Availability Zones** (e.g. `ap-south-1a` and `ap-south-1b`) and select the default public subnet for each.
5. **Security groups**:
   - Remove the default security group.
   - Select **`alb-sg`** (created in Phase 1.1).
6. **Listeners and routing**:
   - **Listener 1 (Port 80 - HTTP)**:
     - Protocol: `HTTP` | Port: `80`
     - Default action: Select **Redirect to URL**
     - Target protocol: `HTTPS` | Port: `443` | Status code: `301 - Permanently moved`
       *(This automatically forces all plain HTTP visitors to HTTPS)*.
   - Click **Add listener** $\rightarrow$ **Listener 2 (Port 443 - HTTPS)**:
     - Protocol: `HTTPS` | Port: `443`
     - Default action: **Forward to target groups** $\rightarrow$ select **`tg-fashion-frontend`**
     - Under **Default SSL/TLS server certificate**:
       - Choose **From ACM** $\rightarrow$ select your `predictoraa.com` certificate (issued in Phase 7).
7. Click **Create load balancer**.
8. Once created, select `alb-fashion-agent`:
   - Click on the **Listeners and rules** tab.
   - Click on the **HTTPS: 443** listener rule.
   - Click **Add rule**:
     - **Name**: `RouteBackendAPI`
     - **Conditions**: Click **Add condition** $\rightarrow$ **Path** $\rightarrow$ Enter paths:
       `/chat*`, `/products*`, `/health*`, `/auth*`
     - **Actions**: Click **Add action** $\rightarrow$ **Forward to target groups** $\rightarrow$ select **`tg-fashion-backend`**.
     - **Priority**: Enter `10`.
     - Click **Save**.

---

## 🎯 Phase 9: Point `predictoraa.com` to the ALB in Route 53

1. In AWS Console $\rightarrow$ Navigate to **Route 53** $\rightarrow$ Click **Hosted zones** $\rightarrow$ Open **`predictoraa.com`**.
2. Click **Create record** (for the root domain `predictoraa.com`):
   - **Record name**: *(Leave completely blank for root apex)*
   - **Record type**: `A`
   - **Alias**: Toggle switch to **ON**.
   - **Route traffic to**: Select **Alias to Application and Classic Load Balancer**.
   - **Choose Region**: Select your ALB's region (e.g., `ap-south-1` Asia Pacific (Mumbai)).
   - **Choose load balancer**: Select your `alb-fashion-agent`.
   - Click **Create records**.
3. Click **Create record** again (for `www.predictoraa.com`):
   - **Record name**: `www`
   - **Record type**: `A`
   - **Alias**: Toggle switch to **ON**.
   - **Route traffic to**: Select **Alias to Application and Classic Load Balancer**.
   - **Choose Region**: Select your region.
   - **Choose load balancer**: Select `alb-fashion-agent`.
   - Click **Create records**.

---

## 🚢 Phase 10: Create Amazon ECS Cluster & Initial Services

### 10.1 Create ECS Cluster
> [!NOTE]
> **Prerequisites for ECS:**
> - If creating an ECS cluster for the first time in your account, ensure the ECS service-linked role exists:
>   ```bash
>   aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
>   ```
> - If you receive an error `Unable to assume the service linked role`, attach this inline policy (`AllowPassRoleForECS`) to your IAM user in the IAM console:
>   ```json
>   {
>     "Version": "2012-10-17",
>     "Statement": [
>       {
>         "Effect": "Allow",
>         "Action": [
>           "iam:PassRole",
>           "iam:GetRole",
>           "iam:ListRoles"
>         ],
>         "Resource": "*"
>       }
>     ]
>   }
>   ```

1. In AWS Console $\rightarrow$ Search for **Elastic Container Service** (ECS).
2. Click **Clusters** (left menu) $\rightarrow$ Click **Create cluster**.
3. **Cluster name**: `fashion-agent-cluster`
4. **Infrastructure**: Choose **AWS Fargate (serverless)**.
5. Click **Create**.

---

### 10.2 Register Initial Task Definitions
Before creating the services, ECS needs the task definition families registered.
Run these two quick AWS CLI commands from your local project root:

```bash
# Register Backend Task Definition (replacing <ACCOUNT_ID> and <REGION>)
aws ecs register-task-definition --cli-input-json file://deploy/ecs-backend-task.json

# Register Frontend Task Definition (replacing <ACCOUNT_ID> and <REGION>)
aws ecs register-task-definition --cli-input-json file://deploy/ecs-frontend-task.json
```
*(Or use the ECS Console $\rightarrow$ Task definitions $\rightarrow$ Create new task definition with JSON).*

---

### 10.3 Create the 2 ECS Fargate Services

#### Create `fashion-backend-service`:
1. In ECS $\rightarrow$ Click **Clusters** $\rightarrow$ Open **`fashion-agent-cluster`** $\rightarrow$ Under **Services** tab click **Create**.
2. **Environment**:
   - **Compute configuration**: Select **`Launch type`** $\rightarrow$ defaults to `FARGATE` (or keep `Capacity provider strategy` with `FARGATE`)
   - **Application type**: `Service`
   - **Task definition**: Family: `fashion-backend` | Revision: `1 (latest)`
   - **Service name**: `fashion-backend-service`
   - **Desired tasks**: `1`
3. **Networking**:
   - **VPC**: Default VPC
   - **Subnets**: Select at least 2 public subnets
   - **Security group**: Select **`ecs-tasks-sg`** (remove `default`)
   - **Public IP**: **Turned ON**
4. **Load balancing**:
   - **Load balancer type**: `Application Load Balancer`
   - **Application Load Balancer**: Choose **Use an existing load balancer** $\rightarrow$ select `alb-fashion-agent`
   - **Container to load balance**: `fashion-backend 8000:8000`
   - **Listener**: Choose **Use an existing listener** $\rightarrow$ select **`HTTPS:443`** *(Note: Do not select HTTP:80 as it only performs redirect)*
   - **Target group**: Choose **Use an existing target group** $\rightarrow$ select **`tg-fashion-backend`**
5. Click **Create**.

#### Create `fashion-frontend-service`:
1. In **`fashion-agent-cluster`** $\rightarrow$ Click **Create** under Services.
2. **Environment**:
   - **Compute configuration**: Select **`Launch type`** $\rightarrow$ `FARGATE`
   - **Application type**: `Service`
   - **Task definition**: Family: `fashion-frontend` | Revision: `1 (latest)`
   - **Service name**: `fashion-frontend-service`
   - **Desired tasks**: `1`
3. **Networking**:
   - **VPC**: Default VPC & at least 2 public subnets
   - **Security group**: Select **`ecs-tasks-sg`** (remove `default`)
   - **Public IP**: **Turned ON**
4. **Load balancing**:
   - **Load balancer type**: `Application Load Balancer`
   - **Application Load Balancer**: Choose **Use an existing load balancer** $\rightarrow$ select `alb-fashion-agent`
   - **Container to load balance**: `fashion-frontend 80:80`
   - **Listener**: Choose **Use an existing listener** $\rightarrow$ select **`HTTPS:443`**
   - **Target group**: Choose **Use an existing target group** $\rightarrow$ select **`tg-fashion-frontend`**
5. Click **Create**.

---

## 🔑 Phase 11: Add GitHub Repository Secrets

Now connect your GitHub Repository to AWS so that GitHub Actions can run builds and deployments.

1. Open your repository on **GitHub** (https://github.com/your-username/sql_fashion_brand_agent).
2. Click **Settings** (tab at the top) $\rightarrow$ In the left menu expand **Secrets and variables** $\rightarrow$ Click **Actions**.
3. Under **Repository secrets**, click **New repository secret** and add these 3 secrets:

| Secret Name | Secret Value |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | The Access Key ID of `github-actions-deployer` (from Phase 5.2) |
| `AWS_SECRET_ACCESS_KEY` | The Secret Access Key of `github-actions-deployer` (from Phase 5.2) |
| `AWS_REGION` | Your target AWS region (e.g. `ap-south-1` or `us-east-1`) |

---

## 🚀 Final Deployment Step: Launching the App!

Once Phases 1 through 11 are completed, your AWS infrastructure and CI/CD pipelines are fully wired!

To deploy your application:
```bash
git add .
git commit -m "feat: setup AWS Fargate CI/CD deployment with predictoraa.com"
git push origin main
```

1. Open your GitHub Repository $\rightarrow$ Click the **Actions** tab.
2. You will see the **CI/CD Pipeline - AWS ECS Fargate** running:
   - ✅ **CI Stage**: Linting with Ruff, formatting with Black, Pytest unit tests pass.
   - ✅ **CD Stage**: Docker images build in the GitHub cloud, push to Amazon ECR, and deploy to AWS Fargate.
3. Open **`https://predictoraa.com`** in your browser to experience STELLA live on your custom domain with full HTTPS security!
