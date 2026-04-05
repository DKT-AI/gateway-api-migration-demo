#!/usr/bin/env bash
set -euo pipefail

# Path 1: Migrate from NGINX Ingress to Gateway API
# Shows the ingress2gateway conversion flow

echo "=== Path 1: NGINX Ingress → Gateway API ==="

# Step 1: Show current NGINX Ingress
echo ""
echo "--- Current NGINX Ingress ---"
kubectl -n gatewaydemo get ingress gatewaydemo -o yaml 2>/dev/null || echo "No NGINX Ingress found"

# Step 2: Run ingress2gateway (if installed)
echo ""
echo "--- Running ingress2gateway ---"
if command -v ingress2gateway &>/dev/null; then
    ingress2gateway print \
        --input-file manifests/02-ingress-nginx/ingress.yaml \
        --output-file manifests/05-migration/nginx-converted-live.yaml
    echo "Conversion output saved to manifests/05-migration/nginx-converted-live.yaml"
    echo ""
    echo "Review the output and compare with manifests/04-gateway-api/"
else
    echo "ingress2gateway not installed. Using pre-generated output."
    echo "See: manifests/05-migration/nginx-converted.yaml"
fi

# Step 3: Deploy Gateway API resources (the migration target)
echo ""
echo "--- Deploying Gateway API resources ---"
kubectl apply -f manifests/04-gateway-api/

# Step 4: Wait for Gateway to be programmed
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
