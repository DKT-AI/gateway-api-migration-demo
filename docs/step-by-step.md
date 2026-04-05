# Step-by-Step Migration Guide

Complete hands-on labs for the DKT episode demo. Each section is self-contained with commands and expected output.

## Prerequisites

- AWS account with EKS, VPC, ALB, ACM, ECR, Route 53 permissions
- `terraform >= 1.5`, `kubectl >= 1.30`, `docker`, [task](https://taskfile.dev)
- Python 3.12+ (for running tests)
- `aws` CLI configured with appropriate credentials

---

## Lab 0: Initial Setup

### 0.1 Clone and provision

```bash
git clone https://github.com/DKT-AI/gateway-api-migration-demo.git
cd gateway-api-migration-demo
```

### 0.2 Provision infrastructure

```bash
task infra:init
task infra:apply
```

Expected: EKS cluster, VPC, ACM certificate, ECR repos, Gateway API CRDs, and AWS LBC provisioned (~15 min).

### 0.3 Configure kubectl

```bash
CLUSTER_NAME=$(cd terraform && terraform output -raw cluster_name)
REGION=$(cd terraform && terraform output -raw region)
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$REGION"
```

Verify:
```bash
kubectl get nodes
# Expected: 2 nodes in Ready state
# NAME                                          STATUS   ROLES    AGE   VERSION
# ip-10-0-x-x.eu-central-1.compute.internal    Ready    <none>   5m    v1.32.x
# ip-10-0-x-x.eu-central-1.compute.internal    Ready    <none>   5m    v1.32.x
```

### 0.4 Substitute ACCOUNT_ID in manifests

```bash
ACCOUNT_ID=$(cd terraform && terraform output -raw account_id)
# Replace placeholder in all manifests
find manifests/ -name '*.yaml' -exec sed -i.bak "s/ACCOUNT_ID/$ACCOUNT_ID/g" {} +
find manifests/ -name '*.bak' -delete

# Replace CERTIFICATE_ARN in ALB ingress
CERT_ARN=$(cd terraform && terraform output -raw acm_certificate_arn)
sed -i.bak "s|CERTIFICATE_ARN|$CERT_ARN|g" manifests/03-ingress-alb/ingress.yaml
rm -f manifests/03-ingress-alb/ingress.yaml.bak
```

### 0.5 Build and push images

```bash
task images:build
task images:push
```

Expected: 3 images built and pushed to ECR.

### 0.6 Deploy base applications

```bash
task deploy:apps
```

Verify:
```bash
kubectl -n gatewaydemo get pods
# Expected:
# NAME                           READY   STATUS    RESTARTS   AGE
# products-v1-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
# products-v1-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
# products-v2-xxxxxxxxxx-xxxxx   1/1     Running   0          30s

kubectl -n gatewaydemo-cart get pods
# Expected:
# NAME                    READY   STATUS    RESTARTS   AGE
# cart-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
# cart-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

---

## Lab 1: Path 1 — NGINX Ingress → Gateway API

**Scenario:** You have ingress-nginx and need to migrate (controller swap).

### 1.1 Deploy NGINX Ingress (starting point)

```bash
task deploy:ingress-nginx
```

Verify:
```bash
kubectl -n gatewaydemo get ingress
# Expected:
# NAME          CLASS   HOSTS                       ADDRESS   PORTS     AGE
# gatewaydemo   nginx   gateway-demo.vedmich.dev              80, 443   10s
```

> **Note:** The cart route in this Ingress will 503 — Ingress cannot reference Services across namespaces. This is a key limitation that Gateway API solves.

### 1.2 Run ingress2gateway conversion

```bash
# Install (if not already)
go install github.com/kubernetes-sigs/ingress2gateway@latest

# Convert and inspect
ingress2gateway print \
  --input-file manifests/02-ingress-nginx/ingress.yaml
```

Expected output: Gateway + HTTPRoute YAML. Compare with `manifests/04-gateway-api/`:
- `gatewayClassName` is empty → needs "alb"
- No traffic splitting (was in annotations)
- No cross-namespace routing (was impossible in Ingress)
- No header-based routing (was canary annotation)

See `manifests/05-migration/nginx-converted.yaml` for the annotated conversion.

### 1.3 Apply Gateway API resources

```bash
kubectl apply -f manifests/04-gateway-api/
```

Verify:
```bash
kubectl -n gatewaydemo get gateway
# Expected:
# NAME          CLASS   ADDRESS                                PROGRAMMED   AGE
# gatewaydemo   alb     k8s-gatewayd-xxxxxx.eu-central-1...   True         60s

kubectl -n gatewaydemo get httproute
# Expected:
# NAME       HOSTNAMES                        PARENTREFS             AGE
# products   ["gateway-demo.vedmich.dev"]     ["gatewaydemo"]        60s
# cart       ["gateway-demo.vedmich.dev"]     ["gatewaydemo"]        60s

kubectl -n gatewaydemo-cart get referencegrant
# Expected:
# NAME                        AGE
# allow-gatewaydemo-routes    60s
```

### 1.4 Test routing

```bash
# Products endpoint
curl -s https://gateway-demo.vedmich.dev/api/products | jq '.[0]'
# Expected: {"id": 1, "name": "Wireless Keyboard", "price": 49.99, "category": "electronics"}

# Cart endpoint (cross-namespace — this NOW works via ReferenceGrant!)
curl -s https://gateway-demo.vedmich.dev/api/cart/demo-user | jq
# Expected: {"user_id": "demo-user", "items": [], "total": 0}
```

### 1.5 Run E2E tests

```bash
task test:e2e
# Expected: all tests pass
```

### 1.6 Cleanup for next lab

```bash
kubectl delete -f manifests/04-gateway-api/
kubectl delete -f manifests/02-ingress-nginx/
```

---

## Lab 2: Path 2 — ALB Ingress → Gateway API

**Scenario:** You have AWS ALB Controller with `kind: Ingress` annotations (API swap).

### 2.1 Deploy ALB Ingress (starting point)

```bash
task deploy:ingress-alb
```

Verify:
```bash
kubectl -n gatewaydemo get ingress
# Expected:
# NAME          CLASS   HOSTS                       ADDRESS                              PORTS   AGE
# gatewaydemo   alb     gateway-demo.vedmich.dev    k8s-gatewayd-xxxxxx.eu-central-1..   80      30s
```

### 2.2 Review annotation → CRD mapping

See the full mapping table:
```bash
cat manifests/05-migration/alb-mapping.yaml
```

Key mappings:

| ALB Annotation | Gateway API Equivalent |
|---|---|
| `scheme` | Gateway annotation |
| `target-type` | TargetGroupConfiguration CRD |
| `certificate-arn` | ACM auto-discovery by hostname |
| `healthcheck-*` | TargetGroupConfiguration healthCheck |
| `actions.*` | HTTPRoute backendRefs weights |

### 2.3 Apply Gateway API resources

```bash
kubectl delete -f manifests/03-ingress-alb/
kubectl apply -f manifests/04-gateway-api/
```

### 2.4 Verify (same as Lab 1, Step 1.4)

```bash
kubectl -n gatewaydemo get gateway,httproute
curl -s https://gateway-demo.vedmich.dev/api/products | jq '.[0]'
```

---

## Lab 3: Demo Scenarios

> All scenarios require `manifests/04-gateway-api/` to be applied.

### 3.1 Traffic Splitting (90/10)

HTTPRoute sends 90% traffic to products-v1 and 10% to products-v2.

```bash
# Send 10 requests — responses come from v1 or v2 based on 90/10 weight
for i in $(seq 1 10); do
  curl -s https://gateway-demo.vedmich.dev/api/products | jq '.[0].name'
done
# Expected: most responses show products (from v1), ~1 may differ
```

Show the HTTPRoute config:
```bash
kubectl -n gatewaydemo get httproute products -o yaml | grep -A5 backendRefs
# Expected:
#   backendRefs:
#   - name: products-v1
#     port: 80
#     weight: 90
#   - name: products-v2
#     port: 80
#     weight: 10
```

### 3.2 Header-Based Routing

`x-version: v2` header routes to products-v2 (which has `/recommendations`).

```bash
# Without header → default routing (v1 or split)
curl -s https://gateway-demo.vedmich.dev/api/products/1 | jq .name
# Expected: "Wireless Keyboard"

# With header → products-v2
curl -s -H "x-version: v2" https://gateway-demo.vedmich.dev/api/products/1 | jq .name
# Expected: "Wireless Keyboard"

# v2-only endpoint: recommendations
curl -s -H "x-version: v2" \
  https://gateway-demo.vedmich.dev/api/products/1/recommendations | jq
# Expected: [{"id": 3, "name": "Laptop Stand", ...}, {"id": 5, "name": "Monitor Light Bar", ...}]

# Without header, recommendations returns 404 (v1 doesn't have this endpoint)
curl -s https://gateway-demo.vedmich.dev/api/products/1/recommendations
# Expected: 404 (most of the time — 10% chance of hitting v2)
```

### 3.3 Cross-Namespace Routing

Cart service lives in `gatewaydemo-cart` namespace. Gateway API routes to it via ReferenceGrant.

```bash
# Show the cross-namespace setup
kubectl -n gatewaydemo-cart get referencegrant
# Expected: allow-gatewaydemo-routes

# Empty cart
curl -s https://gateway-demo.vedmich.dev/api/cart/demo-user | jq
# Expected: {"user_id": "demo-user", "items": [], "total": 0}

# Add item to cart
curl -s -X POST https://gateway-demo.vedmich.dev/api/cart \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","product_id":1,"name":"Wireless Keyboard","price":49.99}' | jq
# Expected: {"user_id": "demo-user", "items": [{"product_id": 1, ...}], "total": 49.99}

# Verify cart persists
curl -s https://gateway-demo.vedmich.dev/api/cart/demo-user | jq .total
# Expected: 49.99
```

### 3.4 Canary Deployment (Progressive Rollout)

Demonstrate changing traffic weights over time.

```bash
# Current state: 90/10 (v1/v2)
kubectl -n gatewaydemo get httproute products -o jsonpath='{.spec.rules[1].backendRefs[*].weight}'
# Expected: 90 10

# Shift to 50/50
kubectl -n gatewaydemo patch httproute products --type=json \
  -p='[{"op":"replace","path":"/spec/rules/1/backendRefs/0/weight","value":50},{"op":"replace","path":"/spec/rules/1/backendRefs/1/weight","value":50}]'

# Verify
kubectl -n gatewaydemo get httproute products -o jsonpath='{.spec.rules[1].backendRefs[*].weight}'
# Expected: 50 50

# Shift to 0/100 (full cutover to v2)
kubectl -n gatewaydemo patch httproute products --type=json \
  -p='[{"op":"replace","path":"/spec/rules/1/backendRefs/0/weight","value":0},{"op":"replace","path":"/spec/rules/1/backendRefs/1/weight","value":100}]'

# Rollback to 90/10
kubectl -n gatewaydemo patch httproute products --type=json \
  -p='[{"op":"replace","path":"/spec/rules/1/backendRefs/0/weight","value":90},{"op":"replace","path":"/spec/rules/1/backendRefs/1/weight","value":10}]'
```

### 3.5 TLS Verification

```bash
# Verify TLS certificate (ACM auto-discovery)
curl -v https://gateway-demo.vedmich.dev/api/products 2>&1 | grep -E 'subject:|issuer:'
# Expected:
# *  subject: CN=gateway-demo.vedmich.dev
# *  issuer: C=US; O=Amazon; CN=Amazon RSA 2048 M03

# Verify HTTPS works
curl -s -o /dev/null -w "%{http_code}" https://gateway-demo.vedmich.dev/api/products
# Expected: 200
```

---

## Cleanup

```bash
scripts/teardown.sh
# Or:
task teardown
```

All AWS resources are tagged `Project=vedmich-gatewaydemo` for easy identification.
Estimated teardown time: ~10 minutes.
