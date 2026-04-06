# Lab 3: Gateway API Demo Scenarios

Hands-on scenarios demonstrating Gateway API capabilities that are impossible or cumbersome with Ingress.

**Duration:** ~20 minutes

**Prerequisite:** Gateway API resources deployed (`kubectl apply -f manifests/04-gateway-api/`).

## Scenarios Overview

```mermaid
flowchart TB
    GW["🌐 Gateway<br/>gatewaydemo<br/>HTTPS :443"]

    subgraph S1["Scenario 1: Traffic Split"]
        HR1["HTTPRoute: products<br/>Rule 2: weighted"]
        HR1 -->|"weight: 90"| V1["products-v1"]
        HR1 -->|"weight: 10"| V2a["products-v2"]
    end

    subgraph S2["Scenario 2: Header Routing"]
        HR2["HTTPRoute: products<br/>Rule 1: header match"]
        HR2 -->|"x-version: v2"| V2b["products-v2<br/>/recommendations"]
    end

    subgraph S3["Scenario 3: Cross-Namespace"]
        HR3["HTTPRoute: cart"]
        HR3 -->|"ReferenceGrant"| CART["🛒 cart<br/>gatewaydemo-cart ns"]
    end

    GW --> HR1
    GW --> HR2
    GW --> HR3

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class GW primary
    class HR1,HR2,HR3 accent
    class V1,CART secondary
    class V2a,V2b tertiary
```

---

## Scenario 3.1: Traffic Splitting (90/10)

HTTPRoute sends 90% of `/api/products` traffic to products-v1 and 10% to products-v2.

### How it works

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#E8F4FD', 'primaryTextColor': '#2C3E50', 'primaryBorderColor': '#2980B9', 'lineColor': '#7F8C8D', 'secondaryColor': '#F0F7EE', 'tertiaryColor': '#F3E8FF', 'actorBkg': '#E8F4FD', 'actorBorder': '#2980B9', 'actorTextColor': '#2C3E50', 'signalColor': '#2C3E50', 'signalTextColor': '#2C3E50'}}}%%
sequenceDiagram
    participant C as 👤 curl
    participant ALB as ☁️ ALB
    participant V1 as products-v1 (90%)
    participant V2 as products-v2 (10%)

    loop 10 requests
        C->>ALB: GET /api/products
        alt 90% probability
            ALB->>V1: forward
            V1-->>C: product list (v1)
        else 10% probability
            ALB->>V2: forward
            V2-->>C: product list (v2)
        end
    end
```

### HTTPRoute config

```bash
kubectl -n gatewaydemo get httproute products -o yaml | grep -A8 'backendRefs'
```

```yaml
# Rule 2: Weighted traffic split
backendRefs:
  - name: products-v1
    port: 80
    weight: 90
  - name: products-v2
    port: 80
    weight: 10
```

### Try it

```bash
# Send 10 requests -- responses come from v1 or v2 based on weights
for i in $(seq 1 10); do
  curl -s https://gateway-demo.vedmich.dev/api/products | jq '.[0].name'
done
```

Expected: most responses return product data. With 90/10 split, ~1 in 10 may differ.

> **Ingress comparison:** NGINX Ingress requires a separate canary Ingress resource with `canary-weight` annotation. ALB Ingress requires a JSON blob in `actions.*` annotation. Gateway API: a typed `weight` field.

---

## Scenario 3.2: Header-Based Routing

The `x-version: v2` header routes requests directly to products-v2, bypassing the traffic split.

### How it works

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#E8F4FD', 'primaryTextColor': '#2C3E50', 'primaryBorderColor': '#2980B9', 'lineColor': '#7F8C8D', 'secondaryColor': '#F0F7EE', 'tertiaryColor': '#F3E8FF', 'actorBkg': '#E8F4FD', 'actorBorder': '#2980B9', 'actorTextColor': '#2C3E50', 'signalColor': '#2C3E50', 'signalTextColor': '#2C3E50', 'noteBkgColor': '#FFF3E0', 'noteTextColor': '#2C3E50', 'noteBorderColor': '#E67E22'}}}%%
sequenceDiagram
    participant C as 👤 curl
    participant ALB as ☁️ ALB
    participant V1 as products-v1
    participant V2 as products-v2

    Note over C,V2: Without header (default routing)
    C->>ALB: GET /api/products
    ALB->>V1: 90% → v1
    V1-->>C: product list

    Note over C,V2: With header (deterministic routing)
    C->>ALB: GET /api/products + x-version: v2
    ALB->>V2: 100% → v2
    V2-->>C: product list

    Note over C,V2: v2-only endpoint
    C->>ALB: GET /api/products/1/recommendations + x-version: v2
    ALB->>V2: → v2
    V2-->>C: recommendations list
```

### HTTPRoute config

HTTPRoute uses **rule ordering** -- the header match rule comes first (higher priority):

```yaml
rules:
  # Rule 1: Header match (evaluated first)
  - matches:
      - path: { type: PathPrefix, value: /api/products }
        headers:
          - name: x-version
            value: v2
    backendRefs:
      - name: products-v2
        port: 80

  # Rule 2: Default with traffic split (fallback)
  - matches:
      - path: { type: PathPrefix, value: /api/products }
    backendRefs:
      - name: products-v1
        port: 80
        weight: 90
      - name: products-v2
        port: 80
        weight: 10
```

### Try it

```bash
# Without header -- default routing (v1 or split)
curl -s https://gateway-demo.vedmich.dev/api/products/1 | jq .name
# Expected: "Wireless Keyboard"

# With header -- deterministic routing to v2
curl -s -H "x-version: v2" https://gateway-demo.vedmich.dev/api/products/1 | jq .name
# Expected: "Wireless Keyboard"

# v2-only endpoint: recommendations (only products-v2 has this)
curl -s -H "x-version: v2" \
  https://gateway-demo.vedmich.dev/api/products/1/recommendations | jq
# Expected:
# [
#   {"id": 3, "name": "Laptop Stand", "reason": "Popular with keyboard buyers"},
#   {"id": 5, "name": "Monitor Light Bar", "reason": "Complete your desk setup"}
# ]

# Without header, /recommendations returns 404 (v1 doesn't have it)
curl -s https://gateway-demo.vedmich.dev/api/products/1/recommendations
# Expected: 404 (most of the time -- 10% chance of hitting v2)
```

> **Use case:** QA team tests v2 via header while production traffic stays on v1. No separate environments needed.

---

## Scenario 3.3: Cross-Namespace Routing

Cart service lives in `gatewaydemo-cart` namespace. Gateway API routes to it via ReferenceGrant.

### How it works

```mermaid
flowchart LR
    subgraph NSMain["Namespace: gatewaydemo"]
        GW["🌐 Gateway"]
        HR["HTTPRoute: cart<br/>backendRef:<br/>namespace: gatewaydemo-cart"]
    end

    subgraph NSCart["Namespace: gatewaydemo-cart"]
        RG["🔑 ReferenceGrant<br/>from: HTTPRoute/gatewaydemo<br/>to: Service"]
        SVC["Service: cart"]
        POD["🛒 cart pods"]
    end

    GW --> HR
    HR -->|"cross-namespace ref"| SVC
    RG -.->|"permits"| HR
    SVC --> POD

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class GW primary
    class HR accent
    class RG tertiary
    class SVC,POD secondary
```

**Security model:** Both sides must agree:
1. **HTTPRoute** (in `gatewaydemo`) declares `namespace: gatewaydemo-cart` in backendRef
2. **ReferenceGrant** (in `gatewaydemo-cart`) explicitly allows HTTPRoutes from `gatewaydemo`

Without the ReferenceGrant, the ALB Controller rejects the route.

### Try it

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
# Expected:
# {
#   "user_id": "demo-user",
#   "items": [{"product_id": 1, "name": "Wireless Keyboard", "price": 49.99, "quantity": 1}],
#   "total": 49.99
# }

# Verify cart persists
curl -s https://gateway-demo.vedmich.dev/api/cart/demo-user | jq .total
# Expected: 49.99
```

> **Ingress comparison:** This is **impossible** with `kind: Ingress` -- Ingress can only reference Services in its own namespace. The cart route in our NGINX/ALB Ingress manifests returns 503.

---

## Scenario 3.4: Canary Deployment (Progressive Rollout)

Demonstrate changing traffic weights live -- zero downtime, no redeployment.

### Rollout plan

```mermaid
flowchart LR
    S90["✅ 90/10<br/>current"]
    S50["⚠️ 50/50<br/>validation"]
    S100["🚀 0/100<br/>full cutover"]

    S90 -->|"kubectl patch"| S50
    S50 -->|"kubectl patch"| S100
    S100 -.->|"rollback"| S90

    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class S90 secondary
    class S50 accent
    class S100 tertiary
```

### Try it

**Check current state (90/10):**

```bash
kubectl -n gatewaydemo get httproute products \
  -o jsonpath='{.spec.rules[1].backendRefs[*].weight}'
# Expected: 90 10
```

**Shift to 50/50:**

```bash
kubectl -n gatewaydemo patch httproute products --type=json \
  -p='[
    {"op":"replace","path":"/spec/rules/1/backendRefs/0/weight","value":50},
    {"op":"replace","path":"/spec/rules/1/backendRefs/1/weight","value":50}
  ]'
```

```bash
kubectl -n gatewaydemo get httproute products \
  -o jsonpath='{.spec.rules[1].backendRefs[*].weight}'
# Expected: 50 50
```

**Full cutover to v2 (0/100):**

```bash
kubectl -n gatewaydemo patch httproute products --type=json \
  -p='[
    {"op":"replace","path":"/spec/rules/1/backendRefs/0/weight","value":0},
    {"op":"replace","path":"/spec/rules/1/backendRefs/1/weight","value":100}
  ]'
```

**Rollback to 90/10:**

```bash
kubectl -n gatewaydemo patch httproute products --type=json \
  -p='[
    {"op":"replace","path":"/spec/rules/1/backendRefs/0/weight","value":90},
    {"op":"replace","path":"/spec/rules/1/backendRefs/1/weight","value":10}
  ]'
```

> **Key point:** Weight changes are applied by the ALB Controller within seconds. No pod restarts, no redeployment. Compare with Ingress where you'd need to modify annotation JSON blobs or manage separate canary Ingress resources.

---

## Scenario 3.5: TLS Verification

```bash
# Verify TLS certificate (ACM auto-discovery)
curl -v https://gateway-demo.vedmich.dev/api/products 2>&1 | grep -E 'subject:|issuer:'
# Expected:
# *  subject: CN=gateway-demo.vedmich.dev
# *  issuer: C=US; O=Amazon; CN=Amazon RSA 2048 M03

# Verify HTTPS returns 200
curl -s -o /dev/null -w "%{http_code}" https://gateway-demo.vedmich.dev/api/products
# Expected: 200
```

> **How it works:** The Gateway listener declares `hostname: gateway-demo.vedmich.dev` and `tls.mode: Terminate`. AWS ALB Controller automatically finds the matching ACM certificate. No certificate ARN annotation, no K8s Secret needed.

---

## Scenario 3.6: Run Full E2E Test Suite

```bash
task test:e2e
```

This runs 6 test files against the live cluster:

| Test File | What It Verifies |
|-----------|-----------------|
| `test_gateway_api.py` | Gateway + HTTPRoutes exist and are programmed |
| `test_traffic_split.py` | Both v1 and v2 receive traffic |
| `test_header_routing.py` | `x-version: v2` routes to v2, recommendations work |
| `test_cross_namespace.py` | Cart accessible cross-namespace |
| `test_ingress_nginx.py` | NGINX Ingress baseline (skip if not deployed) |
| `test_ingress_alb.py` | ALB Ingress baseline (skip if not deployed) |

---

## Cleanup

```bash
# Remove Gateway API resources
kubectl delete -f manifests/04-gateway-api/

# Full teardown (removes EKS, VPC, ACM, ECR -- ~10 min)
task teardown
```

All AWS resources are tagged `Project=vedmich-gatewaydemo` for easy identification.
