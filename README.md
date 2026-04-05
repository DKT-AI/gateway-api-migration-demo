# Gateway API Migration Demo on AWS

Companion demo for [DKT (DevOps Kitchen Talks)](https://youtube.com/@DevOpsKitchenTalks) episode on migrating from Kubernetes Ingress to Gateway API on AWS.

**Slides:** [dkt-ai.github.io/slidev/dkt-gateway-api](https://dkt-ai.github.io/slidev/dkt-gateway-api/)

## What's Inside

Three FastAPI microservices deployed on EKS, demonstrating two migration paths:

- **Path 1:** NGINX Ingress → Gateway API (controller swap)
- **Path 2:** ALB Ingress → ALB Controller + Gateway API (API swap)

### Demo Scenarios

| Scenario | What it shows |
|----------|--------------|
| Traffic splitting | 90/10 between products v1/v2 via HTTPRoute weights |
| Header-based routing | `x-version: v2` → products-v2 |
| Cross-namespace routing | cart service in separate namespace |
| TLS termination | ACM certificate via Gateway |
| Canary deployment | Progressive rollout with HTTPRoute |
| ingress2gateway | Automated conversion + manual patches |

## Architecture

```
services/
  products-v1/    # Catalog (stable)      GET /api/products, GET /api/products/{id}
  products-v2/    # Catalog + recs (canary) + GET /api/products/{id}/recommendations
  cart/           # Cart (cross-ns)       POST /api/cart, GET /api/cart/{user_id}

manifests/
  01-app/             # Deployments, Services
  02-ingress-nginx/   # NGINX Ingress (before)
  03-ingress-alb/     # ALB Ingress (before)
  04-gateway-api/     # Gateway API (after)
  05-migration/       # ingress2gateway output + patches

terraform/            # EKS + VPC + IAM + ACM
tests/                # Unit (pytest+httpx) + E2E
scripts/              # setup.sh, migrate-*.sh, teardown.sh
```

## Prerequisites

- AWS account with permissions for EKS, VPC, ALB, ACM, ECR
- Terraform >= 1.5
- kubectl >= 1.30
- [Task](https://taskfile.dev) (task runner)
- Python 3.12+ (for services and tests)
- Docker (for building images)

## Quick Start

```bash
# 1. Provision infrastructure
task infra:init
task infra:apply

# 2. Build and push images
task images:build
task images:push

# 3. Deploy apps
task deploy:apps

# 4. Deploy NGINX Ingress (Path 1 starting point)
task deploy:ingress-nginx

# 5. Run migration
task migrate:nginx    # Path 1: NGINX → Gateway API
task migrate:alb      # Path 2: ALB Ingress → ALB Gateway API

# 6. Verify
task test:e2e

# 7. Cleanup (by tag vedmich-gatewaydemo)
task teardown
```

## Tags & Labels

All AWS resources tagged with `Project = vedmich-gatewaydemo` for easy cleanup.

K8s labels: `app.kubernetes.io/part-of: vedmich-gatewaydemo`

Namespaces: `gatewaydemo` (main) + `gatewaydemo-cart` (cross-namespace demo)

## Domain

`gateway-demo.vedmich.dev` — ACM certificate + Route 53 (auto-provisioned by Terraform)

## License

MIT
