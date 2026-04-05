#!/usr/bin/env bash
set -euo pipefail

# Teardown script — cleans up ALL demo resources
# Safe to run multiple times

echo "=== Gateway API Migration Demo — Teardown ==="

# 1. Delete K8s resources
echo ""
echo "--- Deleting Kubernetes resources ---"
kubectl delete -f manifests/04-gateway-api/ --ignore-not-found 2>/dev/null || true
kubectl delete -f manifests/03-ingress-alb/ --ignore-not-found 2>/dev/null || true
kubectl delete -f manifests/02-ingress-nginx/ --ignore-not-found 2>/dev/null || true
kubectl delete -f manifests/01-app/ --ignore-not-found 2>/dev/null || true

# 2. Delete namespaces
echo ""
echo "--- Deleting namespaces ---"
kubectl delete namespace gatewaydemo --ignore-not-found 2>/dev/null || true
kubectl delete namespace gatewaydemo-cart --ignore-not-found 2>/dev/null || true

# 3. Terraform destroy
echo ""
echo "--- Destroying infrastructure ---"
cd terraform
terraform destroy -auto-approve
cd ..

echo ""
echo "=== Teardown complete ==="
echo "All resources tagged 'vedmich-gatewaydemo' have been removed."
