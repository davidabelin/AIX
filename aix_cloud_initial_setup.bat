@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set PROJECT_ID=aix-labs
set APP_ENGINE_LOCATION=us-west1
set REGION=us-west1
set RUNTIME_SA=aix-admin@aix-labs.iam.gserviceaccount.com
set KEY_FILE=%~dp0venv\aix-labs-c28515d88d16.json
set BUCKET=%PROJECT_ID%-data

echo.
echo [1/10] Authenticating service account...
if not exist "%KEY_FILE%" (
  echo ERROR: key file not found: %KEY_FILE%
  goto :fatal
)
call gcloud auth activate-service-account %RUNTIME_SA% --key-file="%KEY_FILE%" --project=%PROJECT_ID%
if errorlevel 1 goto :fatal
call gcloud config set account %RUNTIME_SA%
if errorlevel 1 goto :fatal
call gcloud config set project %PROJECT_ID%
if errorlevel 1 goto :fatal
call gcloud auth application-default set-quota-project %PROJECT_ID% >nul 2>nul
set GOOGLE_APPLICATION_CREDENTIALS=%KEY_FILE%

echo.
echo [2/10] Enabling required APIs...
call gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com cloudtasks.googleapis.com storage.googleapis.com secretmanager.googleapis.com sqladmin.googleapis.com --project=%PROJECT_ID%
if errorlevel 1 goto :fatal

echo.
echo [3/10] Creating App Engine app (if missing)...
call gcloud app describe --project=%PROJECT_ID% >nul 2>nul
if errorlevel 1 (
  call gcloud app create --project=%PROJECT_ID% --region=%APP_ENGINE_LOCATION%
  if errorlevel 1 goto :fatal
)

echo.
echo [4/10] Creating storage bucket (if missing)...
call gcloud storage buckets describe gs://%BUCKET% --project=%PROJECT_ID% >nul 2>nul
if errorlevel 1 (
  call gcloud storage buckets create gs://%BUCKET% --project=%PROJECT_ID% --location=%REGION% --uniform-bucket-level-access >nul 2>nul
  if errorlevel 1 (
    set BUCKET=%PROJECT_ID%-data-%RANDOM%
    echo Base bucket name unavailable. Using fallback: %BUCKET%
    call gcloud storage buckets create gs://%BUCKET% --project=%PROJECT_ID% --location=%REGION% --uniform-bucket-level-access
    if errorlevel 1 goto :fatal
  )
)
call gcloud storage buckets update gs://%BUCKET% --project=%PROJECT_ID% --public-access-prevention
if errorlevel 1 goto :fatal

echo.
echo [5/10] Creating Cloud Tasks queues (if missing)...
call gcloud tasks queues describe rps-training --location=%REGION% --project=%PROJECT_ID% >nul 2>nul
if errorlevel 1 (
  call gcloud tasks queues create rps-training --location=%REGION% --project=%PROJECT_ID% --max-dispatches-per-second=1 --max-concurrent-dispatches=1
  if errorlevel 1 goto :fatal
)
call gcloud tasks queues describe c4-training --location=%REGION% --project=%PROJECT_ID% >nul 2>nul
if errorlevel 1 (
  call gcloud tasks queues create c4-training --location=%REGION% --project=%PROJECT_ID% --max-dispatches-per-second=1 --max-concurrent-dispatches=1
  if errorlevel 1 goto :fatal
)

echo.
echo [6/10] Applying IAM bindings...
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member=serviceAccount:%RUNTIME_SA% --role=roles/cloudtasks.enqueuer --quiet
if errorlevel 1 goto :fatal
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member=serviceAccount:%RUNTIME_SA% --role=roles/secretmanager.secretAccessor --quiet
if errorlevel 1 goto :fatal
call gcloud storage buckets add-iam-policy-binding gs://%BUCKET% --member=serviceAccount:%RUNTIME_SA% --role=roles/storage.objectAdmin --quiet
if errorlevel 1 goto :fatal

echo.
echo [7/10] Creating/updating worker token secrets...
for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(48))"') do set RPS_TOKEN=%%i
if not defined RPS_TOKEN goto :fatal
for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(48))"') do set C4_TOKEN=%%i
if not defined C4_TOKEN goto :fatal

call gcloud secrets describe rps-worker-token --project=%PROJECT_ID% >nul 2>nul
if errorlevel 1 (
  echo %RPS_TOKEN%| call gcloud secrets create rps-worker-token --project=%PROJECT_ID% --replication-policy=automatic --data-file=-
  if errorlevel 1 goto :fatal
) else (
  echo %RPS_TOKEN%| call gcloud secrets versions add rps-worker-token --project=%PROJECT_ID% --data-file=-
  if errorlevel 1 goto :fatal
)

call gcloud secrets describe c4-worker-token --project=%PROJECT_ID% >nul 2>nul
if errorlevel 1 (
  echo %C4_TOKEN%| call gcloud secrets create c4-worker-token --project=%PROJECT_ID% --replication-policy=automatic --data-file=-
  if errorlevel 1 goto :fatal
) else (
  echo %C4_TOKEN%| call gcloud secrets versions add c4-worker-token --project=%PROJECT_ID% --data-file=-
  if errorlevel 1 goto :fatal
)

echo.
echo [8/10] Verifying core resources...
call gcloud app describe --project=%PROJECT_ID% --format="value(locationId)"
if errorlevel 1 goto :fatal
call gcloud storage buckets describe gs://%BUCKET% --project=%PROJECT_ID% --format="value(location)"
if errorlevel 1 goto :fatal
call gcloud tasks queues list --location=%REGION% --project=%PROJECT_ID% --format="table(name,state)"
if errorlevel 1 goto :fatal
call gcloud secrets describe rps-worker-token --project=%PROJECT_ID% --format="value(name)"
if errorlevel 1 goto :fatal
call gcloud secrets describe c4-worker-token --project=%PROJECT_ID% --format="value(name)"
if errorlevel 1 goto :fatal

echo.
echo [9/10] App config values:
echo C4_TASKS_PROJECT_ID=%PROJECT_ID%
echo C4_TASKS_LOCATION=%REGION%
echo C4_TASKS_QUEUE=c4-training
echo C4_TRAINING_WORKER_TOKEN_SECRET=projects/%PROJECT_ID%/secrets/c4-worker-token/versions/latest
echo C4_INTERNAL_WORKER_TOKEN_SECRET=projects/%PROJECT_ID%/secrets/c4-worker-token/versions/latest
echo C4_EVENTS_DIR=gs://%BUCKET%/c4/events
echo C4_MODELS_DIR=gs://%BUCKET%/c4/models
echo C4_EXPORTS_DIR=gs://%BUCKET%/c4/exports
echo RPS_TASKS_PROJECT_ID=%PROJECT_ID%
echo RPS_TASKS_LOCATION=%REGION%
echo RPS_TASKS_QUEUE=rps-training
echo RPS_TRAINING_WORKER_TOKEN_SECRET=projects/%PROJECT_ID%/secrets/rps-worker-token/versions/latest
echo RPS_INTERNAL_WORKER_TOKEN_SECRET=projects/%PROJECT_ID%/secrets/rps-worker-token/versions/latest
echo RPS_EVENTS_DIR=gs://%BUCKET%/rps/events
echo RPS_MODELS_DIR=gs://%BUCKET%/rps/models
echo RPS_EXPORTS_DIR=gs://%BUCKET%/rps/exports

echo.
echo [10/10] DONE
goto :eof

:fatal
echo.
echo FAILED. Stop point above.
exit /b 1
