# 🧹 AWS Infrastructure Teardown & Resource Cleanup Guide
### Complete Runbook to Destroy All Cloud Resources and Prevent Ongoing AWS Charges ($0 Bill)

> ⚠️ **IMPORTANT**: Execute the teardown steps in the **exact numerical order** listed below. Some AWS resources (like Security Groups and Target Groups) cannot be deleted while they are still attached to active Load Balancers or ECS Services.

---

## 📑 Teardown Order Summary

| Step | AWS Service | Resources to Delete | CLI Available? |
| :---: | :--- | :--- | :---: |
| **Step 1** | **Amazon ECS** | ECS Services (`fashion-backend-service`, `fashion-frontend-service`) & Cluster | ✅ |
| **Step 2** | **Application Load Balancer** | `alb-fashion-agent` & Target Groups (`tg-fashion-backend`, `tg-fashion-frontend`) | ✅ |
| **Step 3** | **Amazon Route 53** | `A` Alias records, ACM validation CNAME, and Hosted Zone | ✅ |
| **Step 4** | **AWS Certificate Manager (ACM)** | SSL/TLS Certificate for `predictoraa.com` | ✅ |
| **Step 5** | **Amazon ECR** | Container image repositories (`fashion-backend`, `fashion-frontend`) | ✅ |
| **Step 6** | **Amazon CloudWatch** | Log groups (`/ecs/fashion-backend`, `/ecs/fashion-frontend`) | ✅ |
| **Step 7** | **AWS SSM Parameter Store** | All parameters under `/fashion-agent/*` | ✅ |
| **Step 8** | **VPC Security Groups** | `ecs-tasks-sg` and `alb-sg` | ✅ |
| **Step 9** | **AWS IAM** | User `github-actions-deployer` & `ecsTaskExecutionRole` inline policies | ✅ |
| **Step 10** | **GoDaddy & External DBs** | Reset GoDaddy nameservers; stop Aiven MySQL & Supabase | 🌐 UI |

---

## 🚀 Fast 1-Click Teardown (Complete AWS CLI Script)

If you have the AWS CLI configured, you can run this master cleanup script to delete all AWS resources in seconds:

```bash
#!/bin/bash
REGION="ap-south-1"
CLUSTER="fashion-agent-cluster"

echo "⏳ 1. Deleting ECS Services and Cluster..."
aws ecs update-service --cluster $CLUSTER --service fashion-backend-service --desired-count 0 --region $REGION 2>/dev/null
aws ecs update-service --cluster $CLUSTER --service fashion-frontend-service --desired-count 0 --region $REGION 2>/dev/null
aws ecs delete-service --cluster $CLUSTER --service fashion-backend-service --force --region $REGION 2>/dev/null
aws ecs delete-service --cluster $CLUSTER --service fashion-frontend-service --force --region $REGION 2>/dev/null
aws ecs delete-cluster --cluster $CLUSTER --region $REGION 2>/dev/null

echo "⏳ 2. Deleting Load Balancer and Target Groups..."
ALB_ARN=$(aws elbv2 describe-load-balancers --names alb-fashion-agent --region $REGION --query "LoadBalancers[0].LoadBalancerArn" --output text 2>/dev/null)
if [ "$ALB_ARN" != "None" ] && [ -n "$ALB_ARN" ]; then
  aws elbv2 delete-load-balancer --load-balancer-arn "$ALB_ARN" --region $REGION
  echo "Waiting 20 seconds for ALB deletion to complete..."
  sleep 20
fi

TG_BE=$(aws elbv2 describe-target-groups --names tg-fashion-backend --region $REGION --query "TargetGroups[0].TargetGroupArn" --output text 2>/dev/null)
TG_FE=$(aws elbv2 describe-target-groups --names tg-fashion-frontend --region $REGION --query "TargetGroups[0].TargetGroupArn" --output text 2>/dev/null)
[ "$TG_BE" != "None" ] && [ -n "$TG_BE" ] && aws elbv2 delete-target-group --target-group-arn "$TG_BE" --region $REGION
[ "$TG_FE" != "None" ] && [ -n "$TG_FE" ] && aws elbv2 delete-target-group --target-group-arn "$TG_FE" --region $REGION

echo "⏳ 3. Deleting ECR Repositories..."
aws ecr delete-repository --repository-name fashion-backend --force --region $REGION 2>/dev/null
aws ecr delete-repository --repository-name fashion-frontend --force --region $REGION 2>/dev/null

echo "⏳ 4. Deleting CloudWatch Log Groups..."
aws logs delete-log-group --log-group-name "/ecs/fashion-backend" --region $REGION 2>/dev/null
aws logs delete-log-group --log-group-name "/ecs/fashion-frontend" --region $REGION 2>/dev/null

echo "⏳ 5. Deleting SSM Parameters..."
aws ssm delete-parameters --names \
  "/fashion-agent/SENSENOVA_API_KEY" \
  "/fashion-agent/MYSQL_HOST" \
  "/fashion-agent/MYSQL_PORT" \
  "/fashion-agent/MYSQL_USER" \
  "/fashion-agent/MYSQL_PASSWORD" \
  "/fashion-agent/MYSQL_DATABASE" \
  "/fashion-agent/POSTGRES_HOST" \
  "/fashion-agent/POSTGRES_PORT" \
  "/fashion-agent/POSTGRES_USER" \
  "/fashion-agent/POSTGRES_PASSWORD" \
  "/fashion-agent/POSTGRES_DB" \
  "/fashion-agent/POSTGRES_CONN_STR" \
  --region $REGION 2>/dev/null

echo "⏳ 6. Deleting Security Groups..."
ECS_SG=$(aws ec2 describe-security-groups --group-names ecs-tasks-sg --region $REGION --query "SecurityGroups[0].GroupId" --output text 2>/dev/null)
ALB_SG=$(aws ec2 describe-security-groups --group-names alb-sg --region $REGION --query "SecurityGroups[0].GroupId" --output text 2>/dev/null)
[ "$ECS_SG" != "None" ] && [ -n "$ECS_SG" ] && aws ec2 delete-security-group --group-id "$ECS_SG" --region $REGION 2>/dev/null
[ "$ALB_SG" != "None" ] && [ -n "$ALB_SG" ] && aws ec2 delete-security-group --group-id "$ALB_SG" --region $REGION 2>/dev/null

echo "✅ AWS Core Services Teardown Complete!"
```

---

## 🛠️ Step-by-Step UI & CLI Cleanup Guide

---

### Step 1: Delete Amazon ECS Services & Cluster

#### Via AWS Console (UI):
1. Go to **AWS Console** $\rightarrow$ Search for **Elastic Container Service (ECS)**.
2. Click **Clusters** $\rightarrow$ Open **`fashion-agent-cluster`**.
3. Under the **Services** tab:
   - Select `fashion-backend-service` $\rightarrow$ Click **Delete service** $\rightarrow$ Type `delete` $\rightarrow$ Confirm.
   - Select `fashion-frontend-service` $\rightarrow$ Click **Delete service** $\rightarrow$ Type `delete` $\rightarrow$ Confirm.
4. Click **Delete cluster** (top right) $\rightarrow$ Type `delete fashion-agent-cluster` $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
# Force delete both services
aws ecs delete-service --cluster fashion-agent-cluster --service fashion-backend-service --force --region ap-south-1
aws ecs delete-service --cluster fashion-agent-cluster --service fashion-frontend-service --force --region ap-south-1

# Delete cluster
aws ecs delete-cluster --cluster fashion-agent-cluster --region ap-south-1
```

---

### Step 2: Delete Load Balancer & Target Groups

*(⚠️ Delete the Load Balancer before deleting target groups).*

#### Via AWS Console (UI):
1. Go to **EC2 Console** $\rightarrow$ Scroll down the left menu to **Load Balancers**.
2. Select **`alb-fashion-agent`** $\rightarrow$ Click **Actions** $\rightarrow$ Click **Delete load balancer** $\rightarrow$ Confirm.
3. In the left menu, click **Target Groups**:
   - Select **`tg-fashion-backend`** $\rightarrow$ Click **Actions** $\rightarrow$ **Delete** $\rightarrow$ Confirm.
   - Select **`tg-fashion-frontend`** $\rightarrow$ Click **Actions** $\rightarrow$ **Delete** $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
# 1. Delete ALB
ALB_ARN=$(aws elbv2 describe-load-balancers --names alb-fashion-agent --region ap-south-1 --query "LoadBalancers[0].LoadBalancerArn" --output text)
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN --region ap-south-1

# 2. Wait 20 seconds for ALB to release target groups, then delete target groups
sleep 20
TG_BE=$(aws elbv2 describe-target-groups --names tg-fashion-backend --region ap-south-1 --query "TargetGroups[0].TargetGroupArn" --output text)
TG_FE=$(aws elbv2 describe-target-groups --names tg-fashion-frontend --region ap-south-1 --query "TargetGroups[0].TargetGroupArn" --output text)
aws elbv2 delete-target-group --target-group-arn $TG_BE --region ap-south-1
aws elbv2 delete-target-group --target-group-arn $TG_FE --region ap-south-1
```

---

### Step 3: Delete Route 53 Records & Hosted Zone

#### Via AWS Console (UI):
1. Go to **Route 53 Console** $\rightarrow$ Click **Hosted zones** $\rightarrow$ Open **`predictoraa.com`**.
2. > ⚠️ **CRITICAL NOTE ON SELECTING RECORDS**:  
   > AWS **does not allow** deleting default `NS` and `SOA` records individually. If you select all records, the **"Delete records"** button will be greyed out/faded.
   > 
   > **Check ONLY these 3 custom records (leave `NS` and `SOA` unchecked):**
   > - ✅ `predictoraa.com` (`A` Alias record)
   > - ✅ `www.predictoraa.com` (`A` Alias record)
   > - ✅ `_fc080f...` (`CNAME` ACM validation record)
3. Click **Delete records** (top right) $\rightarrow$ Confirm deletion.
4. **Delete the Hosted Zone ($0.50/month savings)**:
   - Once the 3 custom records are deleted (leaving only `NS` and `SOA`), click the **`Delete zone`** button in the top right corner.
   - Type `delete` $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
# List hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name "predictoraa.com." --query "HostedZones[0].Id" --output text | cut -d'/' -f3)

# Delete hosted zone (after records are deleted)
aws route53 delete-hosted-zone --id $ZONE_ID
```

---

### Step 4: Delete ACM SSL Certificate

#### Via AWS Console (UI):
1. Go to **AWS Certificate Manager (ACM)**.
2. Select the certificate for **`predictoraa.com`** / `*.predictoraa.com`.
3. Click **Actions** $\rightarrow$ Click **Delete** $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
CERT_ARN=$(aws acm list-certificates --region ap-south-1 --query "CertificateSummaryList[?DomainName=='predictoraa.com'].CertificateArn" --output text)
aws acm delete-certificate --certificate-arn $CERT_ARN --region ap-south-1
```

---

### Step 5: Delete Amazon ECR Repositories

#### Via AWS Console (UI):
1. Go to **Amazon ECR** $\rightarrow$ Click **Repositories** (left menu).
2. Select **`fashion-backend`** $\rightarrow$ Click **Delete** $\rightarrow$ Type `delete` $\rightarrow$ Confirm.
3. Select **`fashion-frontend`** $\rightarrow$ Click **Delete** $\rightarrow$ Type `delete` $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
aws ecr delete-repository --repository-name fashion-backend --force --region ap-south-1
aws ecr delete-repository --repository-name fashion-frontend --force --region ap-south-1
```

---

### Step 6: Delete CloudWatch Log Groups

#### Via AWS Console (UI):
1. Go to **CloudWatch Console** $\rightarrow$ **Logs** $\rightarrow$ **Log Management**.
2. Select **`/ecs/fashion-backend`** $\rightarrow$ Click **Actions** $\rightarrow$ **Delete log group(s)** $\rightarrow$ Confirm.
3. Select **`/ecs/fashion-frontend`** $\rightarrow$ Click **Actions** $\rightarrow$ **Delete log group(s)** $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
aws logs delete-log-group --log-group-name "/ecs/fashion-backend" --region ap-south-1
aws logs delete-log-group --log-group-name "/ecs/fashion-frontend" --region ap-south-1
```

---

### Step 7: Delete SSM Parameter Store Secrets

#### Via AWS Console (UI):
1. Go to **AWS Systems Manager** $\rightarrow$ Click **Parameter Store** (left menu).
2. Select all parameters starting with **`/fashion-agent/`**.
3. Click **Delete** $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
aws ssm delete-parameters --names \
  "/fashion-agent/SENSENOVA_API_KEY" \
  "/fashion-agent/MYSQL_HOST" \
  "/fashion-agent/MYSQL_PORT" \
  "/fashion-agent/MYSQL_USER" \
  "/fashion-agent/MYSQL_PASSWORD" \
  "/fashion-agent/MYSQL_DATABASE" \
  "/fashion-agent/POSTGRES_HOST" \
  "/fashion-agent/POSTGRES_PORT" \
  "/fashion-agent/POSTGRES_USER" \
  "/fashion-agent/POSTGRES_PASSWORD" \
  "/fashion-agent/POSTGRES_DB" \
  "/fashion-agent/POSTGRES_CONN_STR" \
  --region ap-south-1
```

---

### Step 8: Delete VPC Security Groups

#### Via AWS Console (UI):
1. Go to **VPC Console** $\rightarrow$ Click **Security Groups** (left menu).
2. Select **`ecs-tasks-sg`** $\rightarrow$ Click **Actions** $\rightarrow$ **Delete security group** $\rightarrow$ Confirm.
3. Select **`alb-sg`** $\rightarrow$ Click **Actions** $\rightarrow$ **Delete security group** $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
ECS_SG=$(aws ec2 describe-security-groups --group-names ecs-tasks-sg --region ap-south-1 --query "SecurityGroups[0].GroupId" --output text)
ALB_SG=$(aws ec2 describe-security-groups --group-names alb-sg --region ap-south-1 --query "SecurityGroups[0].GroupId" --output text)

aws ec2 delete-security-group --group-id $ECS_SG --region ap-south-1
aws ec2 delete-security-group --group-id $ALB_SG --region ap-south-1
```

---

### Step 9: Delete Deployer IAM User & Roles

#### Via AWS Console (UI):
1. Go to **IAM Console** $\rightarrow$ Click **Users**.
2. Select **`github-actions-deployer`** $\rightarrow$ Click **Delete** $\rightarrow$ Confirm.
3. Go to **Roles**:
   - If you want to delete `ecsTaskExecutionRole`: Select `ecsTaskExecutionRole` $\rightarrow$ Click **Delete** $\rightarrow$ Confirm.

#### Via AWS CLI:
```bash
# 1. Delete access keys and policies for github-actions-deployer
KEY_ID=$(aws iam list-access-keys --user-name github-actions-deployer --query "AccessKeyMetadata[0].AccessKeyId" --output text 2>/dev/null)
[ -n "$KEY_ID" ] && aws iam delete-access-key --user-name github-actions-deployer --access-key-id "$KEY_ID"

aws iam detach-user-policy --user-name github-actions-deployer --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser 2>/dev/null
aws iam detach-user-policy --user-name github-actions-deployer --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess 2>/dev/null
aws iam delete-user --user-name github-actions-deployer 2>/dev/null
```

---

### Step 10: External Services & Domain Registrar

1. **GoDaddy**:
   - Log into [GoDaddy](https://www.godaddy.com) $\rightarrow$ My Products $\rightarrow$ Domains $\rightarrow$ `predictoraa.com` $\rightarrow$ Manage DNS.
   - Click **Nameservers** $\rightarrow$ Select **I want to use GoDaddy default nameservers** $\rightarrow$ Save.
2. **Aiven Cloud MySQL**:
   - Log into [Aiven Console](https://console.aiven.io) $\rightarrow$ Power off / Delete the MySQL service.
3. **Supabase PostgreSQL**:
   - Log into [Supabase Console](https://supabase.com/dashboard) $\rightarrow$ Settings $\rightarrow$ General $\rightarrow$ Pause / Delete project.

---

## 💰 Billing Verification Checklist

To confirm your AWS account has **0 active billable services**:
1. Open the [AWS Cost Management & Billing Console](https://console.aws.amazon.com/billing/).
2. Click **Bills** $\rightarrow$ Verify current month forecasted spend is **\$0.00**.
3. Check [AWS Resource Explorer](https://console.aws.amazon.com/resource-explorer/) to ensure no orphaned Elastic IPs, NAT Gateways, or EBS volumes remain active.
