# AIX

Assorted Artificial Intelligence Labs umbrella app.

This repository hosts the AIX hub and bridge adapters. Lab implementations stay
in their own repositories and are mounted by interface.

## Bridge strategy

- `rps` remains independent and is mounted under `/rps`.
- `c4` remains independent and is mounted under `/c4`.
- `euclidorithm` remains independent and is mounted under `/euclidorithm`.
- `polyfolds` is mounted under `/polyfolds` with phase-1 job API bridge.
- Large generated datasets are not tracked in this repo by default.
- Lab apps load lazily on first request to their mount path.

## Local setup

1. Create/activate one shared venv for AIX + labs.
2. Install union dependencies:

```powershell
pip install -r requirements.txt
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
$env:AIX_EUCLIDORITHM_REPO = "C:\\path\\to\\geometry\\euclidorithm"
$env:AIX_POLYFOLDS_REPO = "C:\\path\\to\\geometry\\polyfolds"
$env:AIX_POLYFOLDS_JOBS_ROOT = "C:\\path\\to\\aix\\data\\polyfolds_jobs"
```

4. Run AIX:

```powershell
python run.py
```

Then open `http://127.0.0.1:5000/`.

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
