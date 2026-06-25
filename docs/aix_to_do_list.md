# AIX Running List of Assorted Changes

## TO DO **TODAY**

- [] SHRINK the entire AIX webapp repo!
  - Reduce in size every item on every page beneath the "AIX Labs" uber-app (with the *sole* exception of the Clue sub-app, because that one has already been touched).
  - [] The target scale is 75%  of the present size, across the board. That means:
    - font sizes (limits:  6 points min to 36 points **max**)
    - sizes and arrangement of boxes and panels
    - padding inside boxes and panels
    - layout and size of bubbles and buttons
    - etc.: literally, *everything* gets shrunk

- [] THEN, condense and arrange everything so it fits together aesthetically and functionally much better than it did before
  - Spend time getting this part right, the 'feel' of the app
  - Take it beyond the "shrinkage" stage to the "fix" stage
    - Example of a page that needs "arrangement" help beyond simple shrinkage: ![Connect4 Training Page](<Screenshot 2026-05-02 144809.jpg>)

- [] Final UI pass for this action: **BALANCE and PROPORTION** in size and position (all in the same general AIX "style" with each sub-component slightly different in details)
  - [] Smooth over any rough spots from the universal resizing stage.
  
---

## Last Status refresh: 2026-03-26

## AIX

- [x] Footer is supposed to use the copyleft symbol (`U+1F12F`) or `Copyleft.svg`.
  - AIX hub/templates now use `aix_web/static/icons/copyleft.svg`.
  - Euclidyne standalone chrome now uses the copyleft symbol directly.

- [x] Get volume of recorded gameplay data from the unmaintained RPS server at `https://directed-sonar-429119-u2.uw.r.appspot.com/training`.
  - Captured from `https://directed-sonar-429119-u2.uw.r.appspot.com/api/v1/training/readiness?lookback=5`
  - Recorded volume: `55` sessions, `1,823` round rows, `1,552` training samples at `lookback=5`
- [] Delete or reuse `directed-sonar-429119-u2` if it is not going to stay assigned to RPS.
  - [] issue: the active `gcloud` account in this session does not have IAM access on that project, so it could not be inspected or retired safely.

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

## Polyfolds
- [] show examples from dataset; explain why/how each is valid, invalid, or incomplete
- [] data gen and training to happen offline; lab will:
  - [] let users dynamically construct or submit by file their own nets, and the trained NN will evaluate and will offer probabilities it's in one cat or another
  - [] Users can also unfold from 3D shape to 2D net, with connected edges colored the same. The 3D shape can be rotated and manipulated, and users can cliick on edges to indicate which ones to cut (if not possible to unfold as indicated, will hint by flashing edges to cut or reconnect, until a full and *definitely valid* unfolding is possible
- [] do a *deep dive* on the difficulties in generating valid nets, especially the two solids with the tens of thousands of valid nets: what makes those valid, compared to what makes others (non-trivially) invalid? 

## Connect4
- [] curious: will a CNN classifier solve C4?
  - low-priority sub-side-sub-lab
  - Give it a pixel array for the board, classify into "best next move" according to best recorded look-ahead ML-agent play
- [] Docstring everything!

## Expansion

### Other NN's to cover under AIX?
- [] Choose at least one working interactive lab going for EVERY NN design covered in the source material
  - [] generate full list of viable possibilities (whether taken from archived notebooks or something similar but more up-to-date)

### Clue 
- [x] see docs\clue_design.md for vague general notion
- [x] see docs\ClueDeepDive.md for *the whole story*
- [x] develop comprehensive Plan: docs\CLUE_PLAN_alpha.md
- [x] My preferences include:
  - always prefer the most meaningful naming of buckets, and anything else, with as little extraneous noise in names as possible -- should be limited to at most a time stamp, or if necessary to keep names meaningful add only simple numbers like 0000.
  - make a dynamically displayed UI for human gameplay one of the initial priorities
- [x] Deploy online; live link from AIX main page
  - Live on App Engine at `https://aix-labs.uw.r.appspot.com/clue/`
- [x] Move deployed Clue off costly Cloud SQL.
  - AIX now uses `/tmp` SQLite plus Cloud Storage snapshots for low-cost durability.
- [x] Wire production secrets cleanly for deployed Clue.
  - `OPENAI_API_KEY` now resolves through Secret Manager, and the production database URL does too.
- [] Complete Clue checklist at `clue\docs\clue_to_do.md`

### Double-digits
- [x] Deploy online; live link from AIX main page
  - Live on App Engine at `https://aix-labs.uw.r.appspot.com/doubledigits/`
- [x] Build the new standalone `dd` repo as the `doubledigits` AIX arm.
  - Standalone guided Flask lab now lives in `Local_Python\dd`
  - Migrated notebook-derived helpers, examples, narrative inventory, and provenance docs into the new repo
  - AIX now mounts it under `/doubledigits`
- [] Create the first interactive guided web UI instead of keeping notebooks as the product surface.
  - [x] Level 1: single-digit recognition
  - [x] Level 2: two-digit composition
  - [x] Level 3: controlled arithmetic scenes
  - [] Fix unresponsive UI controls
- [] Phase 2:
  - [] add handwriting/canvas input and richer live interaction.
  - [] NN produces its own consistent handwriting styles with encoder/decoder architecture
    - [] use to populate new sets of double-digit and arithmetic training targets (instead of combining several different styles randomly as it is now) and train 
    - [] use for handwritten responses to arithmetic
- [] Docstring all the code!

### Keep affected connected links up to date
- [x] /contact: need small info boxes for clue and dd now too
- [x] /euclidyne: none of the buttons to sub-labs are linked to anything live
