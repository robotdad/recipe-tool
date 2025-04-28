# Vision: Recipe-Tool UX

## Purpose

Give non-developers a simple, guided workspace to **create, execute, and manage “recipes”** (automation blueprints) with zero code.

## Problem Statement

- Today, authoring JSON recipes is intimidating.
- Users struggle to see recipe status, logs, or outputs in one place.
- Re-using or tweaking existing recipes involves manual file edits.

## Guiding Principles

1. **Clarity first** – every screen answers “What’s happening?” in <5 sec.
2. **Progressive disclosure** – advanced options appear only when needed.
3. **Trust but verify** – users can preview and simulate before running.
4. **Composable** – any recipe or step can be cloned and reused.

## Target Users

| Persona         | Need                                  | Example                                           |
| --------------- | ------------------------------------- | ------------------------------------------------- |
| _Product Owner_ | Describe a workflow in plain language | “Turn podcast audio into a blog post every week.” |
| _Ops Engineer_  | Monitor & debug runtime               | Track failures, view logs, re-run steps           |
| _Power User_    | Share and fork recipes                | Publish a template, others adapt                  |

## Success Metrics

- **<10 min** to create first working recipe from scratch.
- **NPS ≥ 60** for recipe monitoring dashboard.
- **≤ 2 clicks** from error notification to rerun fixed step.

## Out-of-Scope (v1)

- Mobile app
- Multi-tenant marketplace
- Fine-grained RBAC (beyond owner/collaborator)
