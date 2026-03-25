# AIX Running List of Assorted Changes

Status refresh: 2026-03-17

## AIX
- [x] Footer is supposed to use the copyleft symbol (`U+1F12F`) or `Copyleft.svg`.
  - AIX hub/templates now use `aix_web/static/icons/copyleft.svg`.
  - Euclidyne standalone chrome now uses the copyleft symbol directly.

- [x] Get volume of recorded gameplay data from the unmaintained RPS server at `https://directed-sonar-429119-u2.uw.r.appspot.com/training`.
  - Captured from `https://directed-sonar-429119-u2.uw.r.appspot.com/api/v1/training/readiness?lookback=5`
  - Recorded volume: `55` sessions, `1,823` round rows, `1,552` training samples at `lookback=5`
- [ ] Delete or reuse `directed-sonar-429119-u2` if it is not going to stay assigned to RPS.
  - Blocked tonight: the active `gcloud` account in this session does not have IAM access on that project, so I could not inspect or retire it safely.

## DRL 
### Legacy URL: `https://drl-web-x2ulcmhaiq-wm.a.run.app/`
- [x] Replace the ugly generated DRL URL as the canonical entry point.
  - Current canonical DRL URL is `https://deeprl-031026.wm.r.appspot.com/`
  - AIX already points to the canonical App Engine URL, and that canonical URL serves the updated chrome
- [x] Change `Back to AIX Hub` to `AIX Labs` and point it to AIX.
  - Verified on the canonical App Engine DRL URL and in the local DRL repo
- [ ] Retire or redirect the legacy Cloud Run URL if it is no longer intended to be public.
  - It still responds, so this is now a deployment/cloud cleanup item rather than an AIX-code item.

## Euclidyne / AIX follow-up
- [x] Update AIX umbrella wiring from `euclidorithm` to the canonical `euclidyne` service and `/euclidyne` path prefix.
- [x] Update the AIX-side files implicated by that rename:
  - `dispatch.yaml`
  - `app.yaml`
  - `aix_cloud_deploy.bat`
  - `aix_web/blueprints/hub.py`
  - `aix_web/labs/euclidorithm_adapter.py` replaced by a canonical `euclidyne` adapter plus compatibility shim
  - AIX tests/docs updated to expect `euclidyne`
- [x] Decide whether old `/euclidorithm/*` URLs should keep working temporarily.
  - Decision: yes
  - Implemented as explicit compatibility redirects from `/euclidorithm/*` to `/euclidyne/*`
  - `dispatch.yaml` now sends legacy `/euclidorithm/*` traffic to the AIX hub so the redirect can happen before public routing fully flips over

## Connect4
- will a CNN classifier solve C4?
 - Give it a pixel array for the board, classify into "best next move" according to best look-ahead ML agent play

## Expansion

### NN's to cover under AIX 
- [] Get at least one working interactive lab going for EVERY NN design covered in the source material

### Clue 
- [] see docs\clue_design.md
- [] see docs\ClueDeepDive.md
- [] develop comprehensive Plan: docs\ClueImplementationPlan.md

### Double-digits
- [] see docs\doubledigits_design.md
- [] see repo 
- [] develop comprehensive Plan: docs\DoubleDigitsImplementationPlan.md