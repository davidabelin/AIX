# AIX

Assorted Artificial Intelligence Labs umbrella app.

This repository hosts the AIX hub and bridge adapters. Lab implementations stay
in their own repositories and are mounted by interface.

## Bridge strategy

- `rps` remains independent and is mounted under `/rps`.
- `drl` remains independent as a sister app; AIX links to it through `/drl/`.
- `c4` remains independent and is mounted under `/c4`.
- `clue` remains independent and is mounted under `/clue`.
- `doubledigits` remains independent and is mounted under `/doubledigits`.
- `euclidyne` remains independent and is mounted under `/euclidyne`.
- `polyfolds` lives in the sibling `pf` repo and is routed under `/polyfolds`.
- Large generated datasets are not tracked in this repo by default.
- Lab apps load lazily on first request to their mount path.

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

- `/healthz` for mount status + runtime warnings.
- `/diagnostics/bridges` for non-secret bridge/config hints.

Legacy RPS absolute API calls are bridged at `/api/v1/*` for compatibility.
Legacy `/euclidorithm/*` links are redirected to `/euclidyne/*` during the transition.

Cloud persistence note:

- On App Engine, AIX uses local SQLite under `/tmp` plus Cloud Storage snapshots
  for low-cost durability. Configure `RPS_DB_SNAPSHOT_URI`, `C4_DB_SNAPSHOT_URI`,
  and `CLUE_DB_SNAPSHOT_URI` when mounting sibling labs through the hub.
- Direct database URLs remain supported by the sibling lab repos for local or
  rollback scenarios, but AIX no longer requires Cloud SQL.

## Cloud deploy

Run the shared deploy helper from the AIX repo root after your usual `gc.bat`
setup:

```powershell
scripts\deploy
```

This wraps `scripts\aix_cloud_deploy.bat`, previews which sibling repos are in
scope, and then deploys the AIX hub plus any lab repo with an `app.aix.yaml`
manifest. App Engine uploads the current local filesystem contents, so
uncommitted edits in `aix`, `clue`, or another sibling lab repo are included in
what goes live.

Clue `v1.9.5` does not change the basic deploy contract. It still deploys via
`clue\app.aix.yaml`, but that manifest now carries the Agents SDK-related env
vars and the built image now includes the `openai-agents` and `aiosqlite`
dependencies from `clue\requirements.txt`.

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
