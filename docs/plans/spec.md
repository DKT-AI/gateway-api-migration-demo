---
aliases: [Gateway API Migration AWS Spec, DKT Gateway API Episode Spec]
date_created: 2026-04-03, 11:00:00
date_modified: 2026-04-03, 16:54:39
tags: [dkt, gateway-api, kubernetes, aws, migration, vedmich-gatewaydemo, spec]
---

# DKT Episode: Kubernetes Gateway API Migration on AWS — Design Spec

## Overview

Подготовка эпизода DKT (DevOps Kitchen Talks) совместно с Александром Довнаром. Тема: миграция с Kubernetes Ingress на Gateway API с фокусом на AWS. Включает deep research, презентацию (dkt-slidev) и полноценное демо на EKS.

## Decisions

| Параметр | Решение |
|---|---|
| Формат | DKT эпизод (Виктор + Александр Довнар) |
| Presentation skill | dkt-slidev |
| Timeline | Нет дедлайна, фокус на качество контента |
| Migration paths | Оба: NGINX Ingress -> GW API + AWS ALB Controller -> GW API |
| Демо | Полноценный EKS, сложное multi-service приложение |
| IaC | Terraform |
| Demo repo | Новый публичный в DKT-AI org |
| Episode # | TBD (определится позже) |
| Container registry | ECR (private, EKS-native pull) |
| Домен | gateway-demo.vedmich.dev (ACM + Route 53) |
| Подход | A (Research-First, последовательный) |

## Pipeline (последовательный)

```
1. Prompt Optimizer     -> оптимизируем research prompt
2. Deep Research        -> NotebookLM (web sources) + локальный deep-research skill
3. Research Synthesis   -> заметка в vault (27-Research/)
4. Outline              -> структура эпизода + согласование
5. Презентация          -> dkt-slidev
6. Demo repo            -> DKT-AI/gateway-api-migration-demo
7. Episode note         -> 32-DKT/32.60-Episodes/
```

Каждый шаг завершается артефактом и review перед переходом к следующему.

## Deep Research — двухуровневый

### Шаг 1: Prompt Optimizer

Формируем один оптимизированный research prompt, покрывающий:

| Тема | Что исследуем |
|---|---|
| Gateway API core | Архитектура (GatewayClass -> Gateway -> HTTPRoute), отличия от Ingress, versioning (v1, v1beta1), GAMMA initiative |
| ingress2gateway 1.0 | Возможности tool, supported providers, limitations, conversion flow |
| Ingress-NGINX retirement | Timeline, что ломается, migration guide |
| AWS ALB Controller + Gateway API | GA announcement, supported features, GatewayClass config, отличия от Ingress annotations |
| AWS NLB + Gateway API | Поддержка TLSRoute/TCPRoute через NLB |
| Практические паттерны | Traffic splitting, header-based routing, cross-namespace routing, TLS termination, canary |
| Подводные камни | Что НЕ поддерживается в Gateway API vs Ingress annotations, known issues |

### Шаг 2: NotebookLM

1. Создаем новый notebook
2. Добавляем 3 URL как sources:
   - https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/
   - https://aws.amazon.com/blogs/networking-and-content-delivery/navigating-the-nginx-ingress-retirement-a-practical-guide-to-migration-on-aws/
   - https://aws.amazon.com/fr/blogs/networking-and-content-delivery/aws-load-balancer-controller-adds-general-availability-support-for-kubernetes-gateway-api/
3. Создаем Note с deep research query (из Prompt Optimizer)
4. Запускаем NotebookLM deep research

Программатически через MCP tools (research_start, source_add, note). Если не сработает — формируем готовый query для ручного запуска.

### Шаг 3: Локальный deep-research skill

- Tavily + Jina параллельно
- Покрывает: AWS docs, GitHub issues, KEPs, community discussions

### Шаг 4: Синтез

Объединяем результаты в: `20-Calendar/27-Research/2026/2026-04-03-Gateway-API-Migration-AWS.md`

## Outline презентации

| Блок | Содержание | ~Слайдов |
|---|---|---|
| Intro | Почему мы об этом говорим, Ingress-NGINX retirement timeline, что случилось в марте 2026 | 3-4 |
| Теория: Gateway API | Архитектура (GatewayClass -> Gateway -> Routes), отличия от Ingress, role-oriented model (infra vs app dev), GAMMA | 8-10 |
| AWS-специфика | ALB Controller + Gateway API GA, GatewayClass конфигурация, что поддерживается, NLB support | 5-7 |
| Path 1: NGINX Ingress -> Gateway API | ingress2gateway tool, conversion flow, что автоматически / что руками | 5-7 |
| Path 2: AWS ALB Ingress -> ALB Controller + Gateway API | Annotations -> HTTPRoute mapping, AWS-native миграция | 5-7 |
| Демо walkthrough | Архитектура демо-приложения, ключевые моменты | 3-4 |
| Подводные камни | Что НЕ работает, known limitations, gotchas | 3-4 |
| Итоги + ресурсы | Checklist миграции, ссылки, demo repo | 2-3 |

Итого: ~35-45 слайдов. Outline финализируется после research.

## Demo: архитектура приложения

### Демо-приложение: Online Store (Python/FastAPI)

Стек как в DKT bot (~/Documents/GitHub/DKT/dkt-news-telegram-bot/): Python 3.14, FastAPI, async, pydantic-settings, structlog. Знакомый аудитории.

| Сервис | Назначение | Endpoints |
|---|---|---|
| products-v1 | Каталог товаров (stable) | GET /api/products, GET /api/products/{id} |
| products-v2 | Каталог + recommendations (canary) | То же + GET /api/products/{id}/recommendations |
| cart | Корзина (отдельный namespace) | POST /api/cart, GET /api/cart/{user_id} |

3 сервиса достаточно для всех демо-сценариев (traffic split, header routing, cross-namespace). Каждый: минимальный FastAPI, health check, Dockerfile, ~100-150 LoC. Images публикуются в ECR (private), EKS тянет нативно через IRSA.

### Паттерны из DKT bot

- Terraform (VPC, subnets, SGs, ALB + TLS через ACM)
- Health check (/health endpoint)
- Docker multi-stage builds
- pydantic-settings для конфигурации
- Structured logging (structlog)

### Демо-сценарии Gateway API

- Traffic splitting (90/10 между products v1/v2)
- Header-based routing (x-version: v2 -> products-v2)
- Cross-namespace routing (cart в отдельном namespace)
- TLS termination через ACM (gateway-demo.vedmich.dev)
- Canary deployment через HTTPRoute weights
- ingress2gateway автоконвертация + ручные доработки

### Тегирование

AWS ресурсы (Terraform tags):
```hcl
locals {
  project = "vedmich-gatewaydemo"
  tags = {
    Project     = "vedmich-gatewaydemo"
    Environment = "demo"
    Owner       = "vedmich"
    Episode     = "dkt-gateway-api"
    ManagedBy   = "terraform"
  }
}
```

K8s ресурсы (labels):
```yaml
labels:
  app.kubernetes.io/part-of: vedmich-gatewaydemo
  app.kubernetes.io/managed-by: kubectl
  demo.vedmich.dev/episode: dkt-gateway-api
```

Namespaces: `gatewaydemo` (основной) + `gatewaydemo-cart` (cross-namespace demo)

### Тестирование (2 уровня)

| Уровень | Фреймворк | Что проверяем |
|---|---|---|
| Unit | pytest + httpx | Каждый сервис отвечает правильно (локально) |
| E2E | pytest + httpx | Routing через Ingress/Gateway API на живом EKS |

E2E тесты (pytest + httpx, не Playwright — это API routing, не UI):
- test_ingress_nginx.py — всё работает через NGINX Ingress (before)
- test_ingress_alb.py — всё работает через ALB Ingress (before)
- test_gateway_api.py — всё работает через Gateway API (after)
- test_traffic_split.py — 90/10 split между products v1/v2
- test_header_routing.py — x-version: v2 -> products-v2
- test_cross_namespace.py — cart в отдельном namespace

E2E запускаются с локальной машины, BASE_URL = https://gateway-demo.vedmich.dev

Open-source reference: httpbin, podinfo, microservices-demo (Google) — переиспользуем рабочие куски.

## Структура demo repo

```
DKT-AI/gateway-api-migration-demo/
  terraform/                # EKS + VPC + IAM + ACM
  services/
    products-v1/            # FastAPI app + Dockerfile
    products-v2/            # FastAPI app + Dockerfile
    cart/                   # FastAPI app + Dockerfile
  manifests/
    01-app/                 # Deployments, Services
    02-ingress-nginx/       # NGINX Ingress (before)
    03-ingress-alb/         # ALB Ingress (before)
    04-gateway-api/         # Gateway API (after)
    05-migration/           # ingress2gateway output + patches
  tests/
    unit/                   # pytest + httpx per service
    e2e/                    # pytest + httpx routing tests vs live EKS
  scripts/
    setup.sh
    migrate-nginx.sh
    migrate-alb.sh
    teardown.sh             # Cleanup по тегу vedmich-gatewaydemo
  docs/
    step-by-step.md         # Пошаговый гайд
  Taskfile.yml              # task runner
  README.md
```

## Артефакты и расположение

| Артефакт | Расположение |
|---|---|
| Research | 20-Calendar/27-Research/2026/2026-04-03-Gateway-API-Migration-AWS.md |
| Spec (этот файл) | 20-Calendar/27-Research/2026/2026-04-03-Gateway-API-Migration-AWS-Spec.md |
| NotebookLM | Notebook (ссылка в research заметке) |
| Презентация (source) | ~/Documents/GitHub/DKT/slidev-theme-dkt/presentations/dkt-gateway-api.md |
| Презентация (live) | https://dkt-ai.github.io/slidev/dkt-gateway-api/ |
| Demo repo | DKT-AI/gateway-api-migration-demo (новый публичный repo) |
| Episode note | 30-Projects/32-DKT/32.60-Episodes/2026/ |

Vault теги: #dkt, #gateway-api, #kubernetes, #aws, #vedmich-gatewaydemo

## Research Gates (decision points) — RESOLVED 2026-04-03

### Gate 1: ALB Controller feature support

**RESOLVED: Все 6 demo-сценариев поддерживаются.**

Traffic splitting, header routing, cross-namespace, TLS/ACM, canary, ingress2gateway — всё работает. Caveats: regex matching bug (#4573), HTTP→HTTPS redirect port bug (#4567) — дизайним демо чтобы избежать или показать workaround.

### Gate 2: ingress2gateway conversion fidelity

**RESOLVED: Два различных пути подтверждены.**

- Path 1 (NGINX → Gateway API): tool-assisted, 30+ annotations, manual fixes для configuration-snippet, regex, auth
- Path 2 (ALB Ingress → ALB Gateway API): ручной маппинг annotations → type-safe CRDs (LoadBalancerConfiguration, TargetGroupConfiguration, ListenerRuleConfiguration). Нет tool support.

### Gate 3: Scope

**RESOLVED: Оставляем оба пути.**

Path 1 = смена контроллера (NGINX → другой). Path 2 = апгрейд API (Ingress → Gateway API) в рамках того же AWS LBC. Фундаментально разные, оба релевантны для аудитории DKT. 35-45 слайдов реалистично.

> Full research synthesis: [[2026-04-03-Gateway-API-Migration-AWS]]

---

## Finalized Outline (post-research)

**Total: ~42 slides** (target 35-45)

---

### Block 1: Intro (4 slides)

**Slide 1 — Cover**
- Title: "От Ingress к Gateway API: миграция на AWS"
- Subtitle: DevOps Kitchen Talks
- Visual: DKT branding, episode number TBD
- Speaker notes: приветствие, представление со-хоста Александр Довнар

**Slide 2 — Почему мы об этом говорим**
- 3 badge items:
  1. ingress-nginx retirement — март 2026
  2. Gateway API v1 — GA, production-ready
  3. AWS Load Balancer Controller v3.0.0 — Gateway API GA support
- Visual: numbered badge list
- Speaker notes: ~50% K8s кластеров используют ingress-nginx, это масштабная миграция

**Slide 3 — Timeline: что произошло**
- Timeline/диаграмма:
  - Jan 29, 2026: K8s Steering Committee statement
  - Feb 2026: Google "End of an Era" blog
  - Mar 20: ingress2gateway 1.0
  - **Mar 31: End of ALL support**
  - Post-retirement: unpatched CVEs
- Visual: горизонтальная timeline (Mermaid или custom)
- Speaker notes: цитата из steering committee, ссылка на blog post

**Slide 4 — Что ломается после 31 марта**
- 4 badge items:
  1. Zero security patches — CVE остаются открытыми
  2. K8s 1.35+ compatibility — может сломаться
  3. No bug fixes — routing issues навсегда
  4. Annotation sprawl — технический долг растёт
- Visual: numbered badge list (warning style)
- Speaker notes: clarification — Ingress API (kind: Ingress) НЕ deprecated, только ingress-nginx controller. AWS ALB Controller продолжает работать с kind: Ingress (#4537)

---

### Block 2: Теория — Gateway API (9 slides)

**Slide 5 — Gateway API: что это?**
- "Ingress 2.0" — expressive, role-oriented, extensible
- 3 ключевых отличия от Ingress:
  1. Роли вместо единого ресурса
  2. Typed routes вместо annotations
  3. Cross-namespace routing из коробки
- Visual: badge list
- Speaker notes: история создания, SIG Network, graduated в CNCF landscape

**Slide 6 — Resource Model (архитектура)**
- Диаграмма: GatewayClass → Gateway → HTTPRoute → Service → Pods
- Показать: cluster-scoped vs namespace-scoped
- Visual: архитектурная диаграмма (Mermaid/Excalidraw)
- Speaker notes: аналогия — GatewayClass как StorageClass, Gateway как PVC, Route как Pod

**Slide 7 — Role-Oriented Design**
- Таблица 3 роли:
  - Infrastructure Provider → GatewayClass
  - Cluster Operator → Gateway
  - Application Developer → HTTPRoute
- Visual: таблица с иконками ролей
- Speaker notes: главное преимущество — app dev не нужны cluster-admin права, может деплоить routes самостоятельно

**Slide 8 — Ingress vs Gateway API: сравнение**
- Side-by-side YAML: Ingress (с annotations) vs Gateway + HTTPRoute
- Показать: annotations → typed fields
- Visual: два code block рядом
- Speaker notes: подсчитать строки annotations в типичном production Ingress (15-20), vs чистый HTTPRoute

**Slide 9 — HTTPRoute: возможности**
- 5 badge items:
  1. Path matching (Exact, Prefix, RegularExpression)
  2. Header matching (case-sensitive values!)
  3. Query parameter matching
  4. Method matching
  5. Weighted backends (traffic splitting)
- Visual: badge list
- Speaker notes: каждый match type с примером YAML

**Slide 10 — ReferenceGrant: cross-namespace routing**
- Диаграмма: HTTPRoute в ns-A → Service в ns-B → ReferenceGrant в ns-B
- "Handshake" model — обе стороны должны согласиться
- Visual: диаграмма с namespace boxes
- Speaker notes: без ReferenceGrant LBC откажет в programming route. Security model.

**Slide 11 — Route Types**
- Таблица:
  - HTTPRoute → HTTP/HTTPS (L7)
  - GRPCRoute → gRPC (L7)
  - TCPRoute → TCP (L4)
  - TLSRoute → TLS passthrough (L4)
  - UDPRoute → UDP (L4)
- Visual: таблица
- Speaker notes: Standard channel (HTTPRoute, GRPCRoute) vs Experimental (TCP/TLS/UDP). Monthly experimental releases.

**Slide 12 — Versioning и Channels**
- Standard channel = GA, stable (v1)
- Experimental channel = alpha, monthly releases
- Conformance profiles — implementations declare feature support
- Visual: 2-column layout
- Speaker notes: Gateway API v1.4 (Nov 2025) — BackendTLSPolicy, Mesh resource. Monthly `monthly-2026.01` releases.

**Slide 13 — GAMMA: Service Mesh**
- Gateway API for Mesh Management and Administration
- Extends Gateway API to east-west traffic
- Same API, different GatewayClass
- Visual: diagram showing north-south (Gateway) + east-west (Mesh)
- Speaker notes: VPC Lattice = AWS implementation of GAMMA patterns. Istio, Linkerd также поддерживают.

---

### Block 3: AWS-специфика (7 slides)

**Slide 14 — AWS Load Balancer Controller v3.0.0**
- GA milestone для Gateway API
- Feature gates: `ALBGatewayAPI=true`, `NLBGatewayAPI=true`
- Prerequisites: CRDs, VPC CNI, IAM
- Visual: badge list (prerequisites)
- Speaker notes: v2.13.0 = first support, v2.14.0 = ALB, v3.0.0 = full GA. Feature gates disabled by default!

**Slide 15 — ALB + Gateway API: L7 routing**
- GatewayClass: `gateway.k8s.aws/alb`
- HTTPRoute / GRPCRoute → ALB
- Поддерживается: path, header, method matching, redirects, rewrites, OIDC auth
- Visual: YAML example (GatewayClass + Gateway + HTTPRoute)
- Speaker notes: OIDC auth — новая фича в v3.0.0, не было в Ingress Gateway API

**Slide 16 — NLB + Gateway API: L4 routing**
- GatewayClass: `gateway.k8s.aws/nlb`
- TCPRoute / UDPRoute / TLSRoute → NLB
- Нельзя смешивать L4 + L7 на одном Gateway
- Visual: YAML example
- Speaker notes: TLS Passthrough bug #4556 — builds TLS listener instead of TCP

**Slide 17 — Type-Safe CRDs (прощай, annotations)**
- Таблица: old annotation → new CRD
  - `scheme` → LoadBalancerConfiguration
  - `target-type` → TargetGroupConfiguration
  - `certificate-arn` → LoadBalancerConfiguration
  - `actions.*` → ListenerRuleConfiguration
- Visual: таблица mapping
- Speaker notes: главное преимущество — validation at apply time, not silent runtime failure. IDE autocomplete.

**Slide 18 — ACM + TLS интеграция**
- Auto-discovery по hostname из Gateway listener
- ARN only (K8s Secrets не поддерживаются)
- Auto-rotation через ACM
- CRD workaround для validation (#4567)
- Visual: diagram Gateway → ACM → Certificate
- Speaker notes: cert discovery for route hostnames — new in v3.0.0

**Slide 19 — VPC Lattice vs ALB: когда что**
- Таблица decision matrix:
  - ALB: North-South, internet-facing, public APIs
  - Lattice: East-West, service-to-service, multi-cluster
  - Hybrid: both in same cluster, different GatewayClass
- Visual: таблица + diagram (ALB external + Lattice internal)
- Speaker notes: cost comparison — Lattice эффективнее при 20+ сервисах. AWS blog reference.

**Slide 20 — Production Patterns: parallel stack migration**
- 5-step process:
  1. Deploy Gateway API alongside Ingress
  2. Both get separate LB IPs
  3. Test new stack
  4. DNS cutover
  5. Rollback = DNS back
- Visual: numbered badge list
- Speaker notes: Qovery опыт — 300+ кластеров, 4-phase rollout. VMware — 8 часов, zero downtime.

---

### Block 4: Path 1 — NGINX Ingress → Gateway API (6 slides)

**Slide 21 — Path 1: обзор**
- Сценарий: у вас ingress-nginx, нужно мигрировать
- Два варианта: ingress2gateway (автоматизация) + ручная доработка
- Visual: flow diagram (Ingress YAML → tool → Gateway API YAML → manual patches → deploy)
- Speaker notes: "migration assistant, not one-shot replacement"

**Slide 22 — ingress2gateway 1.0: что умеет**
- 30+ NGINX annotations supported
- 4 badge items:
  1. Canary (weight, header) → weighted backendRefs
  2. Redirects (SSL, permanent) → RedirectFilter
  3. CORS → CORSFilter
  4. Timeouts → HTTPRoute timeouts (best-effort)
- Visual: badge list
- Speaker notes: changelog reference, supported annotations list

**Slide 23 — ingress2gateway: что НЕ умеет**
- 4 badge items:
  1. `configuration-snippet` — raw NGINX config не транслируется
  2. `proxy-body-size` — нет Gateway API эквивалента
  3. Auth modules (mTLS, LDAP) — нет прямых аналогов
  4. Regex matching — разное поведение (prefix vs exact)
- Visual: badge list (warning style)
- Speaker notes: notification system в tool показывает что не сконвертировалось. Emitter architecture — `--emitter kgateway`, `--emitter envoy-gateway`

**Slide 24 — Regex Gap: главная ловушка**
- NGINX: `/api/v[0-9]` matches `/api/v1`, `/api/v2/users`, `/API/V1`
- Gateway API: exact, case-sensitive matching
- ingress2gateway добавляет `(?i)` и `.*` но нужно проверить вручную
- Visual: side-by-side code comparison
- Speaker notes: [Before You Migrate blog](https://kubernetes.io/blog/2026/02/27/ingress-nginx-before-you-migrate/) — 5 surprising behaviors. ALB bug #4573 — regex вообще не работает!

**Slide 25 — Demo: NGINX → Gateway API (live)**
- Показываем: existing NGINX Ingress → `ingress2gateway print` → review output → apply → test
- Visual: terminal screenshot / code blocks
- Speaker notes: пошаговый walkthrough из demo repo

**Slide 26 — Path 1: итоги**
- Checklist:
  1. Inventory annotations
  2. Run ingress2gateway
  3. Review notifications (untranslatable)
  4. Fix regex, auth, snippets manually
  5. Deploy parallel, DNS cutover
- Visual: checklist
- Speaker notes: "do it now or under pressure when first CVE drops"

---

### Block 5: Path 2 — ALB Ingress → ALB Gateway API (6 slides)

**Slide 27 — Path 2: обзор**
- Сценарий: у вас ALB Controller + kind: Ingress с annotations, хотите Gateway API
- Тот же контроллер (AWS LBC), новый API
- Нет автоматического tool — ручной маппинг
- Visual: flow diagram (Ingress + annotations → manual mapping → Gateway + CRDs)
- Speaker notes: clarification — kind: Ingress NOT deprecated (#4537), но Gateway API = future

**Slide 28 — Annotation → CRD Mapping**
- Таблица: full mapping
  - scheme → LoadBalancerConfiguration
  - target-type → TargetGroupConfiguration
  - certificate-arn → listenerConfigurations[].defaultCertificate
  - waf-acl-id → wafv2AclArn
  - security-groups → securityGroups
  - actions.* → HTTPRoute filters + ListenerRuleConfiguration
  - conditions.* → HTTPRoute matches
  - healthcheck-* → healthCheck.*
- Visual: таблица (большая, может 2 колонки)
- Speaker notes: полная таблица маппинга, ссылка на LBC docs

**Slide 29 — Before: Ingress + Annotations**
- YAML пример: типичный ALB Ingress с 10+ annotations
- Visual: code block (highlighted annotations)
- Speaker notes: посчитать количество строк annotations vs actual routing logic

**Slide 30 — After: Gateway + HTTPRoute + CRDs**
- YAML пример: тот же routing через Gateway API
- GatewayClass + LoadBalancerConfiguration + Gateway + HTTPRoute
- Visual: code block (cleaner, typed)
- Speaker notes: больше YAML файлов, но каждый — typed, validated, role-separated

**Slide 31 — Demo: ALB Ingress → Gateway API (live)**
- Показываем: existing ALB Ingress → manual conversion → apply → test → compare
- Visual: terminal / code
- Speaker notes: walkthrough из demo repo

**Slide 32 — Path 2: итоги**
- Checklist:
  1. List all ALB annotations used
  2. Map to CRDs (table reference)
  3. Create GatewayClass + LoadBalancerConfiguration
  4. Convert Ingress rules → HTTPRoute
  5. Deploy parallel, DNS cutover
- Visual: checklist
- Speaker notes: advantage — type-safe validation catches errors at apply time

---

### Block 6: Demo Walkthrough (4 slides)

**Slide 33 — Demo Architecture**
- Диаграмма: 3 сервиса (products-v1, products-v2, cart)
- 2 namespaces (gatewaydemo, gatewaydemo-cart)
- EKS + ALB + ACM + Route 53
- Visual: архитектурная диаграмма
- Speaker notes: Python/FastAPI, minimal services ~100-150 LoC each, stack like DKT bot

**Slide 34 — Demo Scenarios**
- 6 badge items:
  1. Traffic splitting: 90/10 products v1/v2
  2. Header routing: `x-version: v2` → products-v2
  3. Cross-namespace: cart в отдельном namespace
  4. TLS termination: gateway-demo.vedmich.dev + ACM
  5. Canary: weight shift v1→v2
  6. ingress2gateway: auto-conversion + patches
- Visual: numbered badge list
- Speaker notes: каждый сценарий — отдельный HTTPRoute или модификация existing

**Slide 35 — Demo: Key Commands**
- Code blocks: key `kubectl` commands
  - `kubectl get gateway`, `kubectl get httproute`
  - `kubectl describe gateway` (status, listeners)
  - curl commands для тестирования routing
- Visual: code blocks
- Speaker notes: Taskfile.yml — `task setup`, `task migrate-nginx`, `task test`

**Slide 36 — E2E Tests**
- 6 test files: pytest + httpx
- Before (Ingress) vs After (Gateway API)
- Automated verification
- Visual: test output screenshot / code
- Speaker notes: BASE_URL = https://gateway-demo.vedmich.dev, tests run from local machine

---

### Block 7: Подводные камни (4 slides)

**Slide 37 — Known Bugs (AWS LBC v3.0.0)**
- 4 badge items (top bugs):
  1. #4573: Regex matching → value matching (не regex!)
  2. #4567: HTTPS redirect → port 80 (нужен explicit port)
  3. #4600: Two parentRefs → status errors
  4. #4556: NLB TLS Passthrough → builds TLS listener
- Visual: badge list (danger style)
- Speaker notes: GitHub issue links, workarounds для каждого

**Slide 38 — Architectural Gotchas**
- 4 badge items:
  1. Нельзя смешивать L4+L7 на одном Gateway
  2. Subnet tagging обязателен (kubernetes.io/role/elb)
  3. ACM: только ARN, K8s Secrets не работают
  4. WAF/Shield/Cognito — через CRDs, не через Gateway API standard
- Visual: badge list (warning style)
- Speaker notes: subnet tagging часто забывают, LBC тихо не создаёт ALB

**Slide 39 — Migration Gotchas**
- 4 badge items:
  1. Regex gap: NGINX prefix+case-insensitive vs Gateway API exact+case-sensitive
  2. DNS propagation during cutover — снижайте TTL заранее
  3. ingress2gateway = assistant, не replacement — review output!
  4. ALB annotations не конвертируются автоматически
- Visual: badge list (warning style)
- Speaker notes: real-world stories — VMware 3 gotchas, Qovery backwards compat

**Slide 40 — What's NOT Supported Yet**
- 3 badge items:
  1. BackendTLSPolicy — experimental only
  2. UDP routing — experimental
  3. Performance benchmarks — нет опубликованных данных
- Visual: badge list
- Speaker notes: monthly experimental releases, feature graduation timeline unclear

---

### Block 8: Итоги + Ресурсы (3 slides)

**Slide 41 — Migration Checklist**
- Checklist (6 items):
  1. Inventory: какие Ingress controllers и annotations используются
  2. Choose path: NGINX → Gateway API или ALB Ingress → ALB Gateway API
  3. Enable: LBC v3.0.0, feature gates, CRDs
  4. Convert: ingress2gateway (Path 1) или manual mapping (Path 2)
  5. Test: parallel stack, E2E tests
  6. Cutover: DNS switch, monitor, rollback plan
- Visual: checklist
- Speaker notes: "architecture decisions matter — what served us 5 years ago may become a burden"

**Slide 42 — Ресурсы**
- Links:
  - AWS Blog: ALB Controller Gateway API GA
  - AWS Blog: NGINX retirement migration guide
  - K8s Blog: ingress2gateway 1.0
  - K8s Blog: Before You Migrate (5 behaviors)
  - Demo repo: DKT-AI/gateway-api-migration-demo
  - aws-samples/sample-eks-kubernetes-gateway-api
- Visual: link list + QR code to demo repo
- Speaker notes: все URLs, дополнительные ресурсы

**Slide 43 — Спасибо + Q&A**
- DKT branding
- Social links (Виктор + Александр)
- QR code: demo repo
- Visual: end slide
- Speaker notes: call to action — subscribe, star demo repo

## Reference: существующий контекст в vault

- K8s 1.34/1.35 research: упоминает Ingress-NGINX retirement и ingress2gateway 1.0
- ALB/NLB knowledge: speaker notes из AWS networking 301 workshop
- DKT bot Terraform: VPC, SGs, ALB + TLS паттерны для переиспользования
- DKT bot тесты: pytest + Playwright паттерны
