# Lab 0: Initial Setup

Provision the EKS cluster, build container images, and deploy the base applications.

**Duration:** ~20 minutes (mostly waiting for EKS provisioning)

```mermaid
flowchart LR
    A["① Terraform Init"] --> B["② Terraform Apply<br/>~15 min"]
    B --> C["③ Configure kubectl"]
    C --> D["④ Substitute ACCOUNT_ID"]
    D --> E["⑤ Build & Push Images"]
    E --> F["⑥ Deploy Apps"]
    F --> G["✅ Verify"]

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class A,B primary
    class C,D accent
    class E,F primary
    class G secondary
```

---

## 0.1 Clone the repository

```bash
git clone https://github.com/DKT-AI/gateway-api-migration-demo.git
cd gateway-api-migration-demo
```

## 0.2 Provision infrastructure

```bash
task infra:init
task infra:apply
```

This creates:

```mermaid
flowchart TB
    subgraph TF["🏗️ Terraform Resources"]
        VPC["🌐 VPC 10.0.0.0/16<br/>2 AZs, NAT Gateway"]
        EKS["⚙️ EKS 1.32<br/>2x t3.medium nodes"]
        CRDs["📦 Gateway API CRDs v1.2.1"]
        LBC["☁️ AWS Load Balancer Controller<br/>v1.12.0 + Gateway API"]
        ACM["🔒 ACM Certificate<br/>gateway-demo.vedmich.dev"]
        ECR["📦 ECR Repositories<br/>products-v1, products-v2, cart"]
    end

    VPC --> EKS
    EKS --> CRDs
    CRDs --> LBC
    EKS --> ECR
    EKS --> ACM

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class VPC,EKS primary
    class CRDs,LBC accent
    class ACM,ECR secondary
```

Expected: all resources provisioned (~15 min).

## 0.3 Configure kubectl

```bash
CLUSTER_NAME=$(cd terraform && terraform output -raw cluster_name)
REGION=$(cd terraform && terraform output -raw region)
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$REGION"
```

**Verify:**

```bash
kubectl get nodes
```

```
# Expected:
NAME                                          STATUS   ROLES    AGE   VERSION
ip-10-0-x-x.eu-central-1.compute.internal    Ready    <none>   5m    v1.32.x
ip-10-0-x-x.eu-central-1.compute.internal    Ready    <none>   5m    v1.32.x
```

## 0.4 Substitute ACCOUNT_ID in manifests

All manifests use `ACCOUNT_ID` as a placeholder for the ECR image URLs.

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

## 0.5 Build and push images

```bash
task images:build
task images:push
```

Expected: 3 images built and pushed to ECR (products-v1, products-v2, cart).

## 0.6 Deploy base applications

```bash
task deploy:apps
```

This deploys Deployments and Services into two namespaces:

```mermaid
flowchart TB
    subgraph NSMain["Namespace: gatewaydemo"]
        D1["🚀 Deployment: products-v1<br/>2 replicas"]
        D2["🚀 Deployment: products-v2<br/>1 replica"]
        S1["Service: products-v1<br/>:80 → :8000"]
        S2["Service: products-v2<br/>:80 → :8000"]
        D1 --> S1
        D2 --> S2
    end

    subgraph NSCart["Namespace: gatewaydemo-cart"]
        D3["🚀 Deployment: cart<br/>2 replicas"]
        S3["Service: cart<br/>:80 → :8000"]
        D3 --> S3
    end

    classDef primary fill:#E8F4FD,stroke:#2980B9,stroke-width:2px,color:#2C3E50
    classDef secondary fill:#F0F7EE,stroke:#27AE60,stroke-width:2px,color:#2C3E50
    classDef accent fill:#FFF3E0,stroke:#E67E22,stroke-width:2px,color:#2C3E50
    linkStyle default stroke:#7F8C8D,stroke-width:1.5px

    class D1,D2,D3 primary
    class S1,S2,S3 secondary
```

**Verify:**

```bash
kubectl -n gatewaydemo get pods
```

```
# Expected:
NAME                           READY   STATUS    RESTARTS   AGE
products-v1-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
products-v1-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
products-v2-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

```bash
kubectl -n gatewaydemo-cart get pods
```

```
# Expected:
NAME                    READY   STATUS    RESTARTS   AGE
cart-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
cart-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

---

**Next:** Choose your migration path:
- [Lab 1: NGINX Ingress -> Gateway API](lab-01-nginx-migration.md) (controller swap)
- [Lab 2: ALB Ingress -> Gateway API](lab-02-alb-migration.md) (API swap)
