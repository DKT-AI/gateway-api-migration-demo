# Hands-On Labs

Complete labs for the DKT episode: migrating from Kubernetes Ingress to Gateway API on AWS.

## Architecture

```mermaid
flowchart TB
    subgraph Internet
        User["👤 User / curl"]
    end

    subgraph AWS["☁️ AWS"]
        R53["🌐 Route 53<br/>gateway-demo.vedmich.dev"]
        ACM["🔒 ACM Certificate"]

        subgraph EKS["⚙️ EKS Cluster"]
            subgraph GatewayLayer["Gateway API Layer"]
                GC["GatewayClass<br/>gateway.k8s.aws/alb"]
                GW["Gateway<br/>HTTPS :443"]
                HR1["HTTPRoute: products<br/>header match + 90/10 split"]
                HR2["HTTPRoute: cart<br/>cross-namespace"]
                RG["ReferenceGrant"]
            end

            subgraph NSMain["Namespace: gatewaydemo"]
                V1["products-v1<br/>stable, 2 replicas"]
                V2["products-v2<br/>canary, 1 replica"]
            end

            subgraph NSCart["Namespace: gatewaydemo-cart"]
                Cart["🛒 cart<br/>2 replicas"]
            end
        end

        ALB["Application Load Balancer<br/>internet-facing"]
    end

    User --> R53
    R53 --> ALB
    ALB --> GW
    ACM -.->|auto-discovery| GW
    GC --> GW
    GW --> HR1
    GW --> HR2
    HR1 -->|"90%"| V1
    HR1 -->|"10%"| V2
    HR1 -->|"x-version: v2"| V2
    HR2 -->|"ReferenceGrant"| Cart
    RG -.->|allows| HR2

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    classDef neutral fill:#FFFFFF,stroke:#7F8C8D,stroke-width:1px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class User,R53,ALB primary
    class GC,GW,HR1,HR2,RG accent
    class V1 secondary
    class V2 tertiary
    class Cart secondary
    class ACM primary
```

## Lab Overview

| Lab | Title | Duration | What You Learn |
|-----|-------|----------|----------------|
| [Lab 0](lab-00-setup.md) | Initial Setup | ~20 min | Provision EKS, build images, deploy apps |
| [Lab 1](lab-01-nginx-migration.md) | NGINX Ingress -> Gateway API | ~15 min | Controller swap migration with ingress2gateway |
| [Lab 2](lab-02-alb-migration.md) | ALB Ingress -> Gateway API | ~10 min | API swap migration (annotations -> CRDs) |
| [Lab 3](lab-03-demo-scenarios.md) | Gateway API Scenarios | ~20 min | Traffic split, header routing, cross-ns, canary |

## Prerequisites

- AWS account with EKS, VPC, ALB, ACM, ECR, Route 53 permissions
- `terraform >= 1.5`, `kubectl >= 1.30`, `docker`, [task](https://taskfile.dev)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (for running tests)
- `aws` CLI configured with appropriate credentials

## Quick Start

```bash
git clone https://github.com/DKT-AI/gateway-api-migration-demo.git
cd gateway-api-migration-demo

# Provision everything
task infra:init && task infra:apply   # ~15 min
task images:build && task images:push
task deploy:apps

# Jump to any lab
open docs/labs/lab-01-nginx-migration.md
```

## Demo Scenarios

```mermaid
flowchart LR
    subgraph S1["Scenario 1: Traffic Split"]
        A1["📨 Request"] -->|"90%"| B1["products-v1"]
        A1 -->|"10%"| C1["products-v2"]
    end

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class A1 primary
    class B1 secondary
    class C1 tertiary
```

```mermaid
flowchart LR
    subgraph S2["Scenario 2: Header Routing"]
        A2["📨 Request<br/>x-version: v2"] --> B2["products-v2"]
        A3["📨 Request<br/>no header"] --> C2["products-v1<br/>90/10 split"]
    end

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef tertiary fill:#F3E8FF,stroke:#8E44AD,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class A2 tertiary
    class A3 primary
    class B2 tertiary
    class C2 secondary
```

```mermaid
flowchart LR
    subgraph S3["Scenario 3: Cross-Namespace"]
        A4["HTTPRoute<br/>ns: gatewaydemo"] -->|"ReferenceGrant"| B4["🛒 cart Service<br/>ns: gatewaydemo-cart"]
    end

    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class A4 accent
    class B4 secondary
```

```mermaid
flowchart LR
    subgraph S4["Scenario 4: Canary Rollout"]
        S90["90/10"] -->|"patch"| S50["50/50"]
        S50 -->|"patch"| S100["0/100"]
        S100 -.->|"rollback"| S90
    end

    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    classDef error fill:#FDEDEE,stroke:#E74C3C,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class S90 secondary
    class S50 accent
    class S100 error
```
