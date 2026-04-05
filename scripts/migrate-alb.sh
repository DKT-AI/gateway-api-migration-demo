#!/usr/bin/env bash
set -euo pipefail

# Path 2: Migrate from ALB Ingress to ALB Controller + Gateway API
# Manual migration — same controller, new API

echo "=== Path 2: ALB Ingress → ALB Controller + Gateway API ==="

# Step 1: Show current ALB Ingress
echo ""
echo "--- Current ALB Ingress ---"
kubectl -n gatewaydemo get ingress gatewaydemo -o yaml 2>/dev/null || echo "No ALB Ingress found"

# Step 2: Show annotation mapping
echo ""
echo "--- Annotation → CRD Mapping ---"
echo "See: manifests/05-migration/alb-mapping.yaml"
echo ""
echo "Key mappings:"
echo "  scheme             → Gateway annotation"
echo "  target-type        → TargetGroupConfiguration CRD"
echo "  certificate-arn    → Gateway listener tls"
echo "  healthcheck-*      → TargetGroupConfiguration healthCheck"
echo "  actions.*          → HTTPRoute backendRefs weights"

# Step 3: Deploy Gateway API resources
echo ""
echo "--- Deploying Gateway API resources ---"
kubectl apply -f manifests/04-gateway-api/

# Step 4: Wait for Gateway
echo ""
echo "--- Waiting for Gateway to be programmed ---"
kubectl -n gatewaydemo wait gateway/gatewaydemo \
    --for=condition=Programmed --timeout=120s 2>/dev/null || \
    echo "Waiting for Gateway... (check: kubectl -n gatewaydemo get gateway)"

# Step 5: Show status
echo ""
echo "--- Gateway API Status ---"
kubectl -n gatewaydemo get gateway
kubectl -n gatewaydemo get httproute
kubectl -n gatewaydemo-cart get referencegrant 2>/dev/null || true

echo ""
echo "=== Migration complete! ==="
echo "Run E2E tests: task test:e2e"
echo ""
echo "To rollback: kubectl delete -f manifests/04-gateway-api/"
