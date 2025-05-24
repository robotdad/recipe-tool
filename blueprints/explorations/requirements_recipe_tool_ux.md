# Requirements: Recipe-Tool UX

## 1. Functional Requirements

### 1.1 Recipe Creation

- FR-1.1-1 Rich-text **“Prompt Builder”**: user writes high-level goal; system autogenerates starter JSON.
- FR-1.1-2 **Step Palette**: drag-and-drop common steps (read_files, llm_generate, loop, etc.).
- FR-1.1-3 **Real-time validation** highlighting missing params or invalid Liquid syntax.

### 1.2 Execution & Monitoring

- FR-1.2-1 Run recipe with selected model + params; show live status per step.
- FR-1.2-2 **Timeline view**: chronological list of step executions with duration & token cost.
- FR-1.2-3 “Rerun from step” for failed or edited steps.

### 1.3 Versioning & Collaboration

- FR-1.3-1 Auto-save versions; diff viewer between recipe revisions.
- FR-1.3-2 Share link with **view / edit** modes.
- FR-1.3-3 Comment threads on individual steps.

### 1.4 Templates & Marketplace (MVP)

- FR-1.4-1 Browse gallery of verified recipes (JSON + docs).
- FR-1.4-2 One-click **“Fork & Edit”** into personal workspace.

## 2. Non-Functional Requirements

| ID      | Requirement           | Target            |
| ------- | --------------------- | ----------------- |
| NFR-2.1 | Initial page load     | ≤ 2 s             |
| NFR-2.2 | Concurrent executions | 20 recipes / user |
| NFR-2.3 | Accessibility         | WCAG 2.1 AA       |
| NFR-2.4 | Audit logs retention  | 30 days           |

## 3. User Stories (MoSCoW)

- **Must** As a _Product Owner_ I can describe a workflow in plain English and get a runnable starter recipe.
- **Should** As an _Ops Engineer_ I can see token expenditure per step to control cost.
- **Could** As a _Power User_ I can publish my recipe to a shared gallery.
- **Won’t (v1)** As a _Guest_ I can execute another user’s private recipe.

## 4. UX Notes & Wireframe Hints

- **Home**: “New Recipe” CTA + list of recent runs.
- **Editor**: Split-pane (JSON on right, visual flow on left).
- **Run Screen**: step cards light up green/yellow/red; click card = detail panel.
- **Template Gallery**: tiled cards with tags (LLM, data-pipeline, blog).

## 5. Open Questions

- Which authentication (e.g. Microsoft Entra) will back the share links?
- Do we sandbox step execution on a per-workspace container?
