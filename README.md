# AIX

Assorted Artificial Intelligence Labs umbrella app.

This repository hosts the AIX hub and bridge adapters. Lab implementations stay
in their own repositories and are mounted by interface.

## Bridge strategy

- `rps` remains independent and is mounted under `/rps`.
- `euclidorithm` remains independent and is mounted under `/euclidorithm`.
- `polyfolds` is mounted under `/polyfolds` with a phase-0 web shell.
- Large generated datasets are not tracked in this repo by default.

## Local setup

1. Create/activate one shared venv for AIX + labs.
2. Install union dependencies:

```powershell
pip install -r requirements.txt
```

3. Optional explicit bridge paths (only needed if sibling defaults are not used):

```powershell
$env:AIX_RPS_REPO = "C:\\path\\to\\rps"
$env:AIX_EUCLIDORITHM_REPO = "C:\\path\\to\\geometry\\euclidorithm"
```

4. Run AIX:

```powershell
python run.py
```

Then open `http://127.0.0.1:5000/`.

