# Hands-On Labs

Complete labs for the DKT episode: migrating from Kubernetes Ingress to Gateway API on AWS.

## Architecture

```mermaid
graph TB
    subgraph Internet
        User[User / curl]
    end

    subgraph AWS
        R53[Route 53<br/>gateway-demo.vedmich.dev]
        ACM[ACM Certificate]

        subgraph EKS Cluster
            subgraph "Gateway API Layer"
                GC[GatewayClass<br/>gateway.k8s.aws/alb]
                GW[Gateway<br/>HTTPS :443]
                HR1[HTTPRoute: products<br/>header match + 90/10 split]
                HR2[HTTPRoute: cart<br/>cross-namespace]
                RG[ReferenceGrant]
            end

            subgraph "Namespace: gatewaydemo"
                V1[products-v1<br/>stable, 2 replicas]
                V2[products-v2<br/>canary, 1 replica]
            end

            subgraph "Namespace: gatewaydemo-cart"
                Cart[cart<br/>2 replicas]
            end
        end

        ALB[Application Load Balancer<br/>internet-facing]
    end

    User --> R53
    R53 --> ALB
    ALB --> GW
    ACM -.->|auto-discovery| GW
    GC --> GW
    GW --> HR1
    GW --> HR2
    HR1 -->|90%| V1
    HR1 -->|10%| V2
    HR1 -->|x-version: v2| V2
    HR2 -->|ReferenceGrant| Cart
    RG -.->|allows| HR2
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

## Demo Scenarios Summary

```mermaid
graph LR
    subgraph "Scenario 1: Traffic Split"
        A1[Request] -->|90%| B1[products-v1]
        A1 -->|10%| C1[products-v2]
    end
```

```mermaid
graph LR
    subgraph "Scenario 2: Header Routing"
        A2["Request<br/>x-version: v2"] --> B2[products-v2]
        A3[Request<br/>no header] --> C2[products-v1<br/>90/10 split]
    end
```

```mermaid
graph LR
    subgraph "Scenario 3: Cross-Namespace"
        A4["HTTPRoute<br/>(ns: gatewaydemo)"] -->|ReferenceGrant| B4["cart Service<br/>(ns: gatewaydemo-cart)"]
    end
```

```mermaid
graph LR
    subgraph "Scenario 4: Canary Rollout"
        S1["90/10"] -->|patch| S2["50/50"]
        S2 -->|patch| S3["0/100"]
        S3 -->|rollback| S1
    end
```
