# Step-by-Step Migration Guide

This guide walks through both migration paths demonstrated in the DKT episode.

## Prerequisites

- AWS account with EKS, VPC, ALB, ACM, ECR, Route 53 permissions
- `terraform >= 1.5`, `kubectl >= 1.30`, `docker`, [task](https://taskfile.dev)
- Python 3.12+ (for running tests)

## Initial Setup

```bash
# Clone the repo
git clone https://github.com/DKT-AI/gateway-api-migration-demo.git
cd gateway-api-migration-demo

# Provision infrastructure
scripts/setup.sh
# Or step by step:
task infra:init && task infra:apply
task images:build && task images:push
task deploy:apps
```

## Path 1: NGINX Ingress → Gateway API

**Scenario:** You're using ingress-nginx and need to migrate (controller swap).

### Step 1: Deploy NGINX Ingress (starting point)

```bash
task deploy:ingress-nginx
# Verify:
kubectl -n gatewaydemo get ingress
curl https://gateway-demo.vedmich.dev/api/products
```

### Step 2: Run ingress2gateway

```bash
# Install ingress2gateway (if not already)
go install github.com/kubernetes-sigs/ingress2gateway@latest

# Convert
ingress2gateway print \
  --input-file manifests/02-ingress-nginx/ingress.yaml

# Compare output with manifests/04-gateway-api/
# Key differences:
# - gatewayClassName must be set to "alb"
# - Traffic splitting not in the conversion
# - Cross-namespace routing needs manual setup
# - Header-based routing needs manual setup
```

### Step 3: Apply Gateway API resources

```bash
scripts/migrate-nginx.sh
# Or manually:
kubectl apply -f manifests/04-gateway-api/
```

### Step 4: Verify

```bash
# Check Gateway status
kubectl -n gatewaydemo get gateway
kubectl -n gatewaydemo describe gateway gatewaydemo

# Check HTTPRoutes
kubectl -n gatewaydemo get httproute

# Run E2E tests
task test:e2e
```

### Step 5: DNS cutover

In production, you would:
1. Lower DNS TTL before migration
2. Switch DNS from old LB to new Gateway LB
3. Monitor traffic
4. Rollback = switch DNS back

---

## Path 2: ALB Ingress → ALB Controller + Gateway API

**Scenario:** You're using AWS ALB Controller with `kind: Ingress` annotations (API swap).

### Step 1: Deploy ALB Ingress (starting point)

```bash
task deploy:ingress-alb
# Verify:
kubectl -n gatewaydemo get ingress
```

### Step 2: Map annotations to CRDs

No automated tool exists for this path. See the mapping table:

```
manifests/05-migration/alb-mapping.yaml
```

Key mappings:
| ALB Annotation | Gateway API Equivalent |
|---|---|
| `scheme` | Gateway annotation |
| `target-type` | TargetGroupConfiguration CRD |
| `certificate-arn` | Gateway listener TLS |
| `healthcheck-*` | TargetGroupConfiguration healthCheck |
| `actions.*` | HTTPRoute backendRefs weights |

### Step 3: Apply Gateway API resources

```bash
scripts/migrate-alb.sh
# Or manually:
kubectl apply -f manifests/04-gateway-api/
```

### Step 4: Verify

Same as Path 1, Step 4.

---

## Demo Scenarios

After applying `manifests/04-gateway-api/`:

### Traffic Splitting (90/10)

```bash
# Send 10 requests — responses come from v1 or v2 based on 90/10 weight
for i in $(seq 1 10); do
  curl -s https://gateway-demo.vedmich.dev/api/products | jq '.[0].name'
done
```

### Header-Based Routing

```bash
# Default → products-v1 (or split)
curl https://gateway-demo.vedmich.dev/api/products

# With header → products-v2
curl -H "x-version: v2" https://gateway-demo.vedmich.dev/api/products

# v2 has recommendations
curl -H "x-version: v2" https://gateway-demo.vedmich.dev/api/products/1/recommendations
```

### Cross-Namespace Routing

```bash
# Cart is in gatewaydemo-cart namespace, routed via ReferenceGrant
curl https://gateway-demo.vedmich.dev/api/cart/demo-user

curl -X POST https://gateway-demo.vedmich.dev/api/cart \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","product_id":1,"name":"Wireless Keyboard","price":49.99}'
```

## Cleanup

```bash
scripts/teardown.sh
# Or:
task teardown
```

All AWS resources are tagged `Project=vedmich-gatewaydemo` for easy identification.
