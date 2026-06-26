# AIX

Assorted Artificial Intelligence Labs umbrella app.

This repository hosts the AIX hub and bridge adapters. Lab implementations stay
in their own repositories and are mounted by interface.

## Bridge strategy

- `rps` remains independent and is mounted under `/rps`.
- `drl` remains independent as a sister app; AIX links to it through `/drl/`.
- `c4` remains independent and is mounted under `/c4`.
- `clue` remains independent and is reached under `/clue`.
- `doubledigits` remains independent and is mounted under `/doubledigits`.
- `euclidyne` remains independent and is mounted under `/euclidyne`.
- `polyfolds` lives in the sibling `pf` repo and is routed under `/polyfolds`.
- Large generated datasets are not tracked in this repo by default.
- Local development lazy-loads lab apps on first request to their mount path.
- Cloud AIX treats separately deployed lab services as App Engine-dispatched
  services, so the hub links to the same path prefixes without importing those
  sibling repos into the default service process.

## Local setup

1. Create/activate one shared venv for AIX + labs.
2. Install union dependencies:

```powershell
pip install -r requirements.txt
```

For tests/dev tooling:

```powershell
pip install -r requirements-dev.txt
```

If `polyhedra` fails with `ModuleNotFoundError: No module named 'numpy'`,
install with build isolation disabled after preinstalling core build deps:

```powershell
python -m pip install -U pip setuptools wheel
python -m pip install numpy
python -m pip install polyhedra --no-build-isolation
```

3. Optional explicit bridge paths (only needed if sibling defaults are not used):

```powershell
$env:AIX_RPS_REPO = "C:\\path\\to\\rps"
$env:AIX_C4_REPO = "C:\\path\\to\\c4"
$env:AIX_CLUE_REPO = "C:\\path\\to\\clue"
$env:AIX_DOUBLEDIGITS_REPO = "C:\\path\\to\\dd"
$env:AIX_EUCLIDYNE_REPO = "C:\\path\\to\\geometry\\euclidyne"
$env:AIX_POLYFOLDS_REPO = "C:\\path\\to\\pf\\polyfolds"
$env:AIX_POLYFOLDS_JOBS_ROOT = "C:\\path\\to\\aix\\data\\polyfolds_jobs"
```

4. Run AIX:

```powershell
python run.py
```

Then open `http://127.0.0.1:5000/`.

Useful diagnostics endpoints:

- `/diagnostics/healthz` for mount/dispatch status + runtime warnings.
- `/healthz` remains as a local/dev compatibility alias, but public App Engine
  checks should use `/diagnostics/healthz`.
- `/diagnostics/bridges` for non-secret bridge/config hints.

Legacy RPS absolute API calls are bridged at `/api/v1/*` for compatibility.
Legacy `/euclidorithm/*` links are redirected to `/euclidyne/*` during the transition.

Cloud service note:

- On App Engine, the default AIX service owns the hub, diagnostics, DRL portal,
  and compatibility redirects. Separately deployed lab services such as Clue
  own their own persistence settings and are routed through `dispatch.yaml`.
- `AIX_DISPATCH_SERVICE_LABS` can override the default cloud-dispatched lab
  list for a rollback or diagnostic run.
- Direct database URLs and Cloud Storage snapshots remain supported by sibling
  lab repos, but AIX no longer carries Clue persistence configuration.

## Cloud deploy

Run the shared deploy helper from the AIX repo root after your usual `gc.bat`
setup:

```powershell
scripts\deploy
```

This wraps `scripts\aix_cloud_deploy.bat`, previews which AIX-managed services
are in scope, and then deploys the AIX default service plus dispatch rules.
App Engine uploads the current local filesystem contents, so uncommitted edits
inside an included repo are part of what goes live.

Clue is intentionally excluded from the AIX deploy scripts. Deploy Clue from
the sibling Clue repo with:

```powershell
..\clue\deploy_clue.bat
```

That Clue deploy helper owns its App Engine manifest selection and upload
hygiene checks.

## Polyfolds Phase-1 API

Mounted under `/polyfolds`:

- `GET /polyfolds/api/v1/presets`
- `POST /polyfolds/api/v1/jobs`
- `GET /polyfolds/api/v1/jobs`
- `GET /polyfolds/api/v1/jobs/{job_id}`

Example submit payload:

```json
{
  "kind": "dataset",
  "solid": "tetra",
  "params": {
    "quick": true,
    "n_valid": 200,
    "n_incomplete": 200,
    "n_invalid": 200,
    "seed": 2025
  }
}
```
