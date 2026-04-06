# Lab 1: NGINX Ingress -> Gateway API

**Scenario:** You have ingress-nginx and need to migrate to Gateway API (controller swap).

**Duration:** ~15 minutes

**Prerequisite:** [Lab 0](lab-00-setup.md) completed (apps deployed, images pushed).

## Migration Flow

```mermaid
flowchart TB
    subgraph Before["❌ Before: NGINX Ingress"]
        I["kind: Ingress<br/>class: nginx<br/>+ annotations"]
        I --> SVC1["products-v1"]
        I -.->|"503 cross-ns impossible"| SVC2["🛒 cart<br/>different namespace"]
    end

    subgraph Tool["🔧 ingress2gateway"]
        TOOL["ingress2gateway print<br/>--input-file ingress.yaml"]
    end

    subgraph After["✅ After: Gateway API"]
        GW["Gateway<br/>class: alb"]
        HR1["HTTPRoute: products<br/>90/10 split + header match"]
        HR2["HTTPRoute: cart<br/>cross-namespace"]
        RG["ReferenceGrant"]
        GW --> HR1
        GW --> HR2
        HR1 --> V1["products-v1"]
        HR1 --> V2["products-v2"]
        HR2 -->|"works!"| CART["🛒 cart"]
        RG -.-> HR2
    end

    I -->|"auto-convert"| TOOL
    TOOL -->|"raw output +<br/>manual patches"| GW

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    classDef error fill:#FDEDEE,stroke:#E74C3C,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class I,SVC2 error
    class SVC1 primary
    class TOOL accent
    class GW,HR1,HR2,RG secondary
    class V1,V2,CART secondary
```

## What changes in migration

| Feature | NGINX Ingress | Gateway API |
|---------|--------------|-------------|
| Traffic splitting | Canary annotations (weight) | HTTPRoute `backendRefs` with `weight` |
| Header routing | Canary annotations (header) | HTTPRoute `matches.headers` |
| Cross-namespace | Not possible (503) | ReferenceGrant handshake |
| TLS | K8s Secret (`secretName`) | ACM auto-discovery by hostname |
| Config | Untyped annotations | Typed CRD fields |

---

## Step 1.1: Deploy NGINX Ingress (starting point)

```bash
task deploy:ingress-nginx
```

**Verify:**

```bash
kubectl -n gatewaydemo get ingress
```

```
# Expected:
NAME          CLASS   HOSTS                       ADDRESS   PORTS     AGE
gatewaydemo   nginx   gateway-demo.vedmich.dev              80, 443   10s
```

**Key limitation to observe:**

```yaml
# manifests/02-ingress-nginx/ingress.yaml (excerpt)
paths:
  - path: /api/products
    backend:
      service:
        name: products-v1   # OK - same namespace
        port: { number: 80 }
  - path: /api/cart
    backend:
      service:
        name: cart           # FAILS - cart is in gatewaydemo-cart namespace
        port: { number: 80 } # Ingress cannot cross namespaces -> 503
```

> **Key takeaway:** Ingress cannot reference Services across namespaces. This is a fundamental limitation that Gateway API solves.

## Step 1.2: Run ingress2gateway conversion

```bash
# Install (if not already)
go install github.com/kubernetes-sigs/ingress2gateway@latest

# Convert and inspect
ingress2gateway print \
  --input-file manifests/02-ingress-nginx/ingress.yaml
```

### What the tool generates vs what we need

```mermaid
flowchart LR
    subgraph Raw["⚠️ Tool Output"]
        direction TB
        G1["Gateway<br/>gatewayClassName: empty<br/>tls: K8s Secret"]
        H1["HTTPRoute<br/>single rule, no split<br/>no header match, no cross-ns"]
    end

    subgraph Patches["✏️ Manual Patches Needed"]
        direction TB
        P1["gatewayClassName: alb"]
        P2["Remove certificateRefs<br/>ACM auto-discovery"]
        P3["Add 90/10 traffic split"]
        P4["Add header-based routing"]
        P5["Add cart HTTPRoute<br/>+ ReferenceGrant"]
    end

    G1 --> P1
    G1 --> P2
    H1 --> P3
    H1 --> P4
    H1 --> P5

    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class G1,H1 accent
    class P1,P2,P3,P4,P5 secondary
```

Compare the raw output (`manifests/05-migration/nginx-converted.yaml`) with the final result (`manifests/04-gateway-api/`):

```bash
diff manifests/05-migration/nginx-converted.yaml manifests/04-gateway-api/gateway.yaml
```

**Key gaps in tool output:**
- `gatewayClassName` is empty -- needs `"alb"`
- TLS uses K8s Secret -- AWS ALB Controller uses ACM auto-discovery
- No traffic splitting -- was commented-out annotations
- No cross-namespace routing -- was impossible in Ingress
- No header-based routing -- was canary annotation

> **Takeaway:** ingress2gateway is a migration *assistant*, not a one-shot replacement. Always review and patch the output.

## Step 1.3: Apply Gateway API resources

The patched, production-ready manifests are in `manifests/04-gateway-api/`:

```bash
kubectl apply -f manifests/04-gateway-api/
```

This creates 5 resources:

```mermaid
flowchart TB
    GC["GatewayClass: alb<br/><i>cluster-scoped</i><br/>controllerName: gateway.k8s.aws/alb"]

    subgraph NSMain["Namespace: gatewaydemo"]
        GW["🌐 Gateway: gatewaydemo<br/>HTTPS :443<br/>hostname: gateway-demo.vedmich.dev"]
        HR1["HTTPRoute: products<br/>Rule 1: x-version:v2 → v2<br/>Rule 2: 90/10 split"]
        HR2["HTTPRoute: cart<br/>→ cart.gatewaydemo-cart"]
    end

    subgraph NSCart["Namespace: gatewaydemo-cart"]
        RG["🔑 ReferenceGrant<br/>allow-gatewaydemo-routes"]
    end

    GC --> GW
    GW --> HR1
    GW --> HR2
    RG -.->|"permits cross-ns ref"| HR2

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class GC primary
    class GW accent
    class HR1,HR2 secondary
    class RG tertiary
```

**Verify:**

```bash
kubectl -n gatewaydemo get gateway
```

```
# Expected:
NAME          CLASS   ADDRESS                                PROGRAMMED   AGE
gatewaydemo   alb     k8s-gatewayd-xxxxxx.eu-central-1...   True         60s
```

```bash
kubectl -n gatewaydemo get httproute
```

```
# Expected:
NAME       HOSTNAMES                        PARENTREFS             AGE
products   ["gateway-demo.vedmich.dev"]     ["gatewaydemo"]        60s
cart       ["gateway-demo.vedmich.dev"]     ["gatewaydemo"]        60s
```

```bash
kubectl -n gatewaydemo-cart get referencegrant
```

```
# Expected:
NAME                        AGE
allow-gatewaydemo-routes    60s
```

## Step 1.4: Test routing

**Products endpoint:**

```bash
curl -s https://gateway-demo.vedmich.dev/api/products | jq '.[0]'
```

```json
{"id": 1, "name": "Wireless Keyboard", "price": 49.99, "category": "electronics"}
```

**Cart endpoint (cross-namespace -- this NOW works via ReferenceGrant!):**

```bash
curl -s https://gateway-demo.vedmich.dev/api/cart/demo-user | jq
```

```json
{"user_id": "demo-user", "items": [], "total": 0}
```

## Step 1.5: Run E2E tests

```bash
task test:e2e
```

Expected: all tests pass.

## Step 1.6: Cleanup (before next lab)

```bash
kubectl delete -f manifests/04-gateway-api/
kubectl delete -f manifests/02-ingress-nginx/
```

---

**Next:** [Lab 2: ALB Ingress -> Gateway API](lab-02-alb-migration.md) or skip to [Lab 3: Demo Scenarios](lab-03-demo-scenarios.md)
