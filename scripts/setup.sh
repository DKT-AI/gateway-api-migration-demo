#!/usr/bin/env bash
set -euo pipefail

# Setup script for Gateway API Migration Demo
# Prerequisites: aws cli, terraform, kubectl, task, docker

echo "=== Gateway API Migration Demo — Setup ==="

# 1. Terraform init + apply
echo ""
echo "--- Step 1: Provisioning infrastructure (EKS + VPC + ACM + ECR) ---"
cd terraform
terraform init
terraform apply -auto-approve
cd ..

# 2. Configure kubectl
echo ""
echo "--- Step 2: Configuring kubectl ---"
CLUSTER_NAME=$(cd terraform && terraform output -raw cluster_name)
REGION=$(cd terraform && terraform output -raw region)
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$REGION"

# 3. Wait for nodes
echo ""
echo "--- Step 3: Waiting for nodes to be ready ---"
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# 4. Build and push images
echo ""
echo "--- Step 4: Building and pushing container images ---"
task images:build
task images:push

# 5. Deploy base apps
echo ""
echo "--- Step 5: Deploying applications ---"
task deploy:apps

# Wait for rollout
echo ""
echo "--- Waiting for deployments to be ready ---"
kubectl -n gatewaydemo rollout status deployment/products-v1 --timeout=120s
kubectl -n gatewaydemo rollout status deployment/products-v2 --timeout=120s
kubectl -n gatewaydemo-cart rollout status deployment/cart --timeout=120s

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  task deploy:ingress-nginx   # Path 1: NGINX Ingress"
echo "  task deploy:ingress-alb     # Path 2: ALB Ingress"
echo "  task deploy:gateway-api     # Gateway API (migration target)"
