# DKT Gateway API Migration — Implementation Plan

> **For agentic workers:** Execute this plan task-by-task, sequentially. NO parallel work. Each task produces an artifact that must be reviewed before proceeding to the next. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare a complete DKT episode (research + presentation + demo repo + episode note) about migrating from Kubernetes Ingress to Gateway API on AWS.

**Architecture:** Sequential content pipeline — each step feeds the next. Research informs outline, outline drives slides, slides reference demo repo. All artifacts land in the Obsidian vault per Johnny Decimal rules.

**Spec:** `20-Calendar/27-Research/2026/2026-04-03-Gateway-API-Migration-AWS-Spec.md`

**Co-host:** Aleksandr Dovnar (AWS Community Builder, CNCF Ambassador, Kubestronaut)

---

## Task 1: Deep Research — NotebookLM [STEP 2a from spec]

**Artifacts:**
- NotebookLM notebook with 3 URL sources + research note
- Research output (saved to vault or referenced by link)

**Prerequisite:** Spec complete (Task 0 DONE)

- [ ] **Step 1: Create NotebookLM notebook**

Use `mcp__notebooklm-mcp__notebook_create` with name: "DKT — Gateway API Migration on AWS"

- [ ] **Step 2: Add 3 URL sources**

Add these URLs via `mcp__notebooklm-mcp__source_add` (source_type=url):
1. `https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release/`
2. `https://aws.amazon.com/blogs/networking-and-content-delivery/navigating-the-nginx-ingress-retirement-a-practical-guide-to-migration-on-aws/`
3. `https://aws.amazon.com/fr/blogs/networking-and-content-delivery/aws-load-balancer-controller-adds-general-availability-support-for-kubernetes-gateway-api/`

- [ ] **Step 3: Create research note in NotebookLM**

Use `mcp__notebooklm-mcp__note` to create a note with the optimized research query covering all 7 research areas from the spec (Gateway API core, ingress2gateway 1.0, Ingress-NGINX retirement, AWS ALB Controller, AWS NLB, practical patterns, gotchas).

- [ ] **Step 4: Run NotebookLM deep research**

Use `mcp__notebooklm-mcp__research_start`. Poll `research_status` until complete.

- [ ] **Step 5: Extract and save NotebookLM results**

Query the notebook for key findings. Save raw output for synthesis in Task 3.

**Review gate:** Show user NotebookLM findings summary before proceeding.

---

## Task 2: Deep Research — Local (Tavily + Jina) [STEP 2b from spec]

**Artifacts:**
- Deep research report: covers AWS docs, GitHub issues, KEPs, community discussions

**Prerequisite:** Task 1 reviewed

- [ ] **Step 1: Formulate research query**

Based on the 7 research areas from the spec, create a focused query for the `deep-research` skill. Focus on areas NotebookLM may have missed: GitHub issues, KEP status, community pain points, AWS-specific limitations.

- [ ] **Step 2: Run deep-research skill**

Invoke `deep-research` skill with the query. This uses Tavily + Jina dual-engine with parallel subagents.

- [ ] **Step 3: Save research output**

Save as interim artifact for synthesis.

**Review gate:** Show user local research findings summary. Identify gaps vs NotebookLM.

---

## Task 3: Research Synthesis + Research Gates [STEP 3 from spec]

**Artifacts:**
- Create: `20-Calendar/27-Research/2026/2026-04-03-Gateway-API-Migration-AWS.md`

**Prerequisite:** Tasks 1 + 2 reviewed

- [ ] **Step 1: Merge research sources**

Combine NotebookLM output + local deep-research into one structured note. Organize by the 7 research topics from the spec.

- [ ] **Step 2: Pass Research Gates**

Evaluate 3 decision points from the spec:

| Gate | Question | Impact |
|------|----------|--------|
| ALB Controller feature support | Which of 6 demo scenarios actually work with ALB Controller + Gateway API GA? | Adjusts demo scope |
| ingress2gateway conversion fidelity | Does tool convert AWS-specific annotations (target-type, health-check, WAF ACL)? | Changes Path 1 narrative |
| Scope: one or two paths | Are both migration paths deep enough for 35-45 slides? | May focus on one path |

- [ ] **Step 3: Write synthesis note**

Create `2026-04-03-Gateway-API-Migration-AWS.md` with:
- Frontmatter (aliases, dates, tags: dkt, gateway-api, kubernetes, aws)
- Structured findings per topic
- Research Gates decisions with evidence
- Links to sources (NotebookLM notebook link, web URLs)
- Verification callout with dates

- [ ] **Step 4: Update spec with gate decisions**

Edit the spec file to record gate decisions (they affect downstream tasks).

**Review gate:** User reviews synthesis + gate decisions. These determine presentation scope and demo architecture.

---

## Task 4: Outline [STEP 4 from spec]

**Artifacts:**
- Presentation outline (section of synthesis note or separate section in spec)

**Prerequisite:** Task 3 gate decisions approved

- [ ] **Step 1: Draft outline based on spec template**

Use the outline table from spec (8 blocks, ~35-45 slides) as starting point. Adjust based on Research Gate decisions:
- If Gate 3 narrowed to one path: redistribute slides
- If Gate 1 limited ALB features: adjust demo scenarios section
- If Gate 2 showed tool limitations: adjust Path 1 narrative

- [ ] **Step 2: Add per-slide detail**

For each block, list specific slides with:
- Slide title
- Key points (3-5 bullets)
- Visual type (diagram, code, screenshot, badge list)
- Speaker notes hints

- [ ] **Step 3: Add to spec or synthesis note**

Append finalized outline to the spec file under a new `## Finalized Outline` section.

**Review gate:** User approves outline before slide creation begins.

---

## Task 5: Presentation — dkt-slidev [STEP 5 from spec]

**Artifacts:**
- Create: `~/Documents/GitHub/DKT/slidev-theme-dkt/presentations/dkt-gateway-api/slides.md`

**Prerequisite:** Task 4 outline approved

- [ ] **Step 1: Invoke dkt-slidev skill**

Use the `dkt-slidev` skill with the approved outline and research synthesis as input. Skill handles: theme setup, slide generation, component usage.

- [ ] **Step 2: Verify slide count and structure**

Check slides match outline (target ~35-45). Verify:
- Numbered badge lists (not plain bullets)
- v-mark with object syntax + color
- Mascots at opacity-[0.12]
- Code blocks >22 lines have maxHeight
- Speaker notes with MAX info (quotes, URLs, alternatives, bonus facts)

- [ ] **Step 3: Preview locally**

Run Slidev dev server, verify rendering, presenter mode at localhost:3030/presenter/

**Review gate:** User reviews slides in presenter mode before demo repo work begins.

---

## Task 6: Demo Repo [STEP 6 from spec]

**Artifacts:**
- Create: `~/Documents/GitHub/DKT/gateway-api-migration-demo/` (local)
- Remote: `DKT-AI/gateway-api-migration-demo` (public GitHub repo)

**Prerequisite:** Task 5 reviewed (slides may reference demo structure)

- [ ] **Step 1: Create repo structure**

Follow spec's repo layout:
```
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
  e2e/                    # pytest + httpx routing tests
scripts/
  setup.sh, migrate-nginx.sh, migrate-alb.sh, teardown.sh
docs/step-by-step.md
Taskfile.yml
README.md
```

- [ ] **Step 2: Implement services (products-v1, products-v2, cart)**

Each: minimal FastAPI, ~100-150 LoC, health check, Dockerfile, pydantic-settings, structlog. Stack like DKT bot.

- [ ] **Step 3: Write Terraform (EKS + VPC + ACM)**

Reuse patterns from DKT bot. Tags: project=vedmich-gatewaydemo. Domain: gateway-demo.vedmich.dev

- [ ] **Step 4: Write K8s manifests (all 5 stages)**

01-app through 05-migration. Labels per spec.

- [ ] **Step 5: Write unit tests**

pytest + httpx for each service.

- [ ] **Step 6: Write E2E tests**

6 test files per spec (ingress_nginx, ingress_alb, gateway_api, traffic_split, header_routing, cross_namespace).

- [ ] **Step 7: Write scripts + docs + Taskfile**

setup.sh, migrate-*.sh, teardown.sh (cleanup by tag vedmich-gatewaydemo), step-by-step.md, README.

- [ ] **Step 8: Create GitHub repo and push**

Create `DKT-AI/gateway-api-migration-demo` (public), push initial commit.

**Review gate:** User reviews repo structure and code before episode note.

---

## Task 7: Episode Note [STEP 7 from spec]

**Artifacts:**
- Create: `30-Projects/32-DKT/32.60-Episodes/2026/YYYY-MM-DD-DKT-Gateway-API-Migration.md`

**Prerequisite:** Tasks 5 + 6 reviewed

- [ ] **Step 1: Create episode note**

Frontmatter: aliases, dates, tags (dkt, gateway-api, kubernetes, aws, episode), status: planning, episode number: TBD.

Content:
- Episode overview
- Links to all artifacts (spec, research, slides URL, demo repo)
- Demo scenarios list
- Recording checklist
- Post-production checklist (YouTube description, Telegram post — future dkt-podcast skill)

- [ ] **Step 2: Update DKT MOC**

Add episode reference to `30-Projects/32-DKT/+ DKT.md` (or relevant MOC).

**Review gate:** Final review. All 7 pipeline artifacts complete.

---

## Artifact Summary

| # | Artifact | Location | Status |
|---|----------|----------|--------|
| 0 | Spec | `27-Research/2026/2026-04-03-Gateway-API-Migration-AWS-Spec.md` | DONE |
| 1 | Plan (this file) | `27-Research/2026/2026-04-03-Gateway-API-Migration-AWS-Plan.md` | DONE |
| 2 | Research (synthesis) | `27-Research/2026/2026-04-03-Gateway-API-Migration-AWS.md` | PENDING |
| 3 | Outline | Appended to spec under `## Finalized Outline` | PENDING |
| 4 | Presentation | `~/Documents/GitHub/DKT/slidev-theme-dkt/presentations/dkt-gateway-api/slides.md` | PENDING |
| 5 | Demo repo | `DKT-AI/gateway-api-migration-demo` | PENDING |
| 6 | Episode note | `32-DKT/32.60-Episodes/2026/` | PENDING |
