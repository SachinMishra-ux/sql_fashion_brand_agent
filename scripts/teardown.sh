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