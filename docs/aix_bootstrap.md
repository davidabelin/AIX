# AIX Bootstrap Notes

Date: 2026-02-28

## Locked decisions applied

1. Bridge strategy: independent repos + package/interface bridge (no file copy).
2. Naming: use `polyfolds` only.
3. Dataset policy: large generated datasets are excluded by default.
4. Environment: one shared venv with union dependencies.

## Initial scaffold delivered

1. Hub app in `aix_web` with landing page and health route.
2. Lazy lab loading so mounted apps import only on first request.
3. Legacy compatibility redirects:
   - `/play` -> `/rps/play`
   - `/training` -> `/rps/training`
   - `/rl` -> `/rps/rl`
4. Lab registry + mount resolution with per-lab error capture.
5. Bridge adapters:
   - `rps` adapter imports `rps_web.create_app()`.
   - `euclidorithm` adapter imports external Flask app.
   - `polyfolds` adapter serves a phase-1 job UI + API shell.
6. WSGI dispatcher mounts labs at:
   - `/rps`
   - `/euclidorithm`
   - `/polyfolds`

## Next implementation phase

1. Add tests for Polyfolds API submit/list/get contracts.
2. Add SSE/live event stream for Polyfolds job updates.
3. Add typed adapter config (`RPS_*`, `EUCLID_*`, `POLYFOLDS_*`) with validation.
