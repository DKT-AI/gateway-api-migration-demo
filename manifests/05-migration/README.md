# Migration Stage

This directory contains the output of migration tools and manual patches.

## Path 1: NGINX Ingress → Gateway API

1. `nginx-converted.yaml` — raw output from `ingress2gateway print`
2. Manual patches applied to get to `04-gateway-api/` final state

## Path 2: ALB Ingress → ALB Gateway API

1. `alb-mapping.yaml` — manually converted from ALB annotations to Gateway API + CRDs
2. Shows the annotation → CRD type-safe mapping

## How to use

These files are for **reference only** — they show the migration process.
The actual working manifests are in `04-gateway-api/`.
