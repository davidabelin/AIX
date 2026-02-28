# AIX Multi-Lab Expansion Plan (RPS + Euclidorithm + Polyfolding)

## Summary
This plan creates a new umbrella Flask app named `aix` that hosts multiple AI labs under path prefixes (`/rps/*`, `/euclidorithm/*`, `/polyfolding/*`) while preserving and reusing your current RPS implementation with minimal disruption.  
Route compatibility is preserved by redirecting old RPS root routes (`/play`, `/training`, `/rl`) to `/rps/*`.

## A) Fork This Conversation Now (practical method)
1. Create a repo checkpoint before branching conversation context:
   - Create a git branch for this point (example: `checkpoint/rps-ui-pass2`).
   - Optional tag for easy return.
2. Start a new chat/conversation window and paste:
   - Branch name.
   - Current objective (“AIX multi-lab expansion”).
   - This plan block.
3. Keep this conversation unchanged as your RPS-focused thread.
4. If your UI has a built-in duplicate/fork action, use that first; if not, use the branch + new chat workflow above (it is the reliable equivalent).

## C) Original Plan Status (where we are now)

### Milestone completion snapshot
1. Milestone 0 (scaffold/app factory/base pages): **Complete**.
2. Milestone 1 (notebook archaeology + heuristic migration): **Complete enough for production use**.
3. Milestone 2 (engine + deterministic simulation/tournaments): **Complete**.
4. Milestone 3 (human-vs-AI page): **Complete**.
5. Milestone 4 (supervised pipeline + model registry): **Complete**.
6. Milestone 5 (training UI + job lifecycle): **Complete**.
7. Milestone 6 (deployment hardening/App Engine/Cloud Tasks/Cloud SQL/Secret Manager): **Mostly complete**.
8. Milestone 7 (RL page + RL training): **Complete for current scope** (tabular RL implementation is functioning).

### Intended-but-not-fully-finished items
1. True split worker as a separate deployable service is not yet fully separated from the web service.
2. Cross-browser validation is not fully closed (especially iOS Safari priority level noted earlier).
3. Some polish/documentation and final acceptance criteria remain operational rather than architectural.

### Minimum remaining to declare original RPS aim “done”
1. Run and close final UX/device acceptance matrix (Desktop Chrome, Android Chrome, iOS Safari basic play flow).
2. Freeze RPS v1 API and route behavior with a release checklist.
3. Decide whether “separate worker service” is mandatory for v1 completion or deferred to v1.1.

## D) Expansion Plan for `geometry/` and new top-level app

## Decisions locked
1. App shape: **One Flask app**.
2. Path scheme: **Lab prefixes** (`/rps/*`, `/euclidorithm/*`, `/polyfolding/*`).
3. Geometry intake: **Wrap then refactor**.
4. Route compatibility: **Redirect old routes**.
5. Top-level app/package name: **`aix`**.

## Target architecture
1. Add a new umbrella package: `aix_web`.
2. Keep existing RPS packages (`rps_web`, `rps_core`, `rps_agents`, `rps_training`, `rps_rl`, `rps_storage`) intact initially.
3. Add lab adapters in `aix_web` that mount each lab under URL prefixes.
4. Gradually normalize `geometry/euclidorithm` and `geometry/polyfolding` to the same shell conventions used by RPS.

## Ideal local file structure (target state)
1. `aix_web/__init__.py` (new app factory).
2. `aix_web/lab_registry.py` (lab metadata and registration contract).
3. `aix_web/blueprints/hub.py` (global splash/home and shared navigation).
4. `aix_web/blueprints/routes_compat.py` (legacy redirect routes).
5. `aix_web/templates/base_hub.html` (shared shell).
6. `aix_web/static/css/hub_theme.css` (shared theme tokens + lab overrides).
7. `aix_web/labs/rps_adapter.py` (mount existing RPS blueprints at `/rps`).
8. `aix_web/labs/euclidorithm_adapter.py` (mount geometry/euclidorithm first as wrapped module).
9. `aix_web/labs/polyfolding_adapter.py` (initial placeholder + data/training module bridge).
10. `geometry/euclidorithm/*` (existing code retained initially, wrapped).
11. `geometry/polyfolding/*` (existing/ongoing data-generation assets retained initially).

## Important changes/additions to public APIs/interfaces/types
1. New URL contract:
   - `/` => AIX hub page.
   - `/rps/*` => existing RPS pages/APIs.
   - `/euclidorithm/*` => Euclidorithm lab pages/APIs.
   - `/polyfolding/*` => Polyfolding lab pages/APIs.
2. Backward-compat redirects:
   - `/play` -> `/rps/play`
   - `/training` -> `/rps/training`
   - `/rl` -> `/rps/rl`
3. New lab registration interface:
   - `LabSpec(slug, display_name, blueprint, nav_order, theme_tokens, enabled)`
   - One registry function to register all enabled labs.
4. Shared UI contract:
   - Every lab page extends shared hub base template.
   - Lab-specific color tokens override shared CSS variables only.

## Reuse strategy (maximum reuse, minimum breakage)
1. Reuse current RPS code as-is via adapter mounting first.
2. Reuse `rps_web/static/css/theme.css` concepts by extracting only shared variables/components to hub theme.
3. Preserve existing RPS API endpoints and job system under `/rps/api/v1/*`.
4. Introduce geometry labs in “compatibility mode” first, then progressively refactor internals.

## Cloud migration path (for future separate GCP project)
1. New App Engine service/project for AIX with same deployment model as RPS.
2. Keep per-lab env prefixes in config:
   - `RPS_*`, `EUCLID_*`, `POLY_*` (storage paths, DB URLs, queues, secrets).
3. Secret Manager naming convention:
   - `aix-rps-database-url`, `aix-euclid-database-url`, `aix-poly-database-url`, etc.
4. Cloud Tasks queue split by lab:
   - `rps-training`, `polyfolding-training` (euclidorithm queue only if needed).
5. Cloud Storage split by lab prefix:
   - `gs://<bucket>/rps/...`
   - `gs://<bucket>/euclidorithm/...`
   - `gs://<bucket>/polyfolding/...`
6. Keep RPS cloud deployment stable during AIX build; do not couple cutover dates.

## Implementation phases (high-level, not code-level detail)
1. Phase 0: Scaffold `aix_web` shell and hub homepage.
2. Phase 1: Mount RPS under `/rps/*` via adapter and add legacy redirects.
3. Phase 2: Add `geometry/euclidorithm` wrapper routes and shared shell integration.
4. Phase 3: Add `geometry/polyfolding` wrapper with placeholder web lab + data hooks.
5. Phase 4: Shared theming + navigation consistency pass across all labs.
6. Phase 5: AIX deployment config for new GCP project (staging first).

## Test cases and scenarios
1. Routing:
   - `/rps/play`, `/euclidorithm`, `/polyfolding` all resolve.
   - `/play`, `/training`, `/rl` redirect correctly to `/rps/*`.
2. UI shell:
   - Shared nav works on desktop/mobile with no horizontal overflow.
3. Lab isolation:
   - RPS APIs still work unchanged under `/rps/api/v1/*`.
   - Geometry modules do not break RPS runtime imports.
4. Data paths:
   - Per-lab storage paths and secrets resolve independently.
5. Deployment:
   - Local Flask start for AIX works.
   - App Engine staging deploy for AIX starts and serves hub + labs.

## Explicit assumptions and defaults
1. `geometry/` will be added soon and initially may not match RPS conventions.
2. We prioritize architectural compatibility first, deep geometry refactors second.
3. RPS remains the production-stable lab while AIX is built.
4. We treat split worker separation as optional for AIX v1 unless explicitly required.
5. We avoid mass file moves in the first integration pass to reduce regression risk.
