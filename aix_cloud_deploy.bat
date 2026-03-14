@echo off
setlocal
call "%~dp0aix_cloud_env.bat"
pushd "%~dp0" >nul 2>&1
if errorlevel 1 goto :fail
set "AIX_ROOT=%CD%"
set "RPS_ROOT=%AIX_ROOT%\..\rps"
set "C4_ROOT=%AIX_ROOT%\..\c4"
set "EUCLID_ROOT=%AIX_ROOT%\..\geometry\euclidorithm"
set "PF_ROOT=%AIX_ROOT%\..\pf"

echo.
echo ==== AIX App Engine Deploy ====
echo Project : %PROJECT_ID%
echo Region  : %REGION%
echo Hub     : %SERVICE_NAME%
echo DRL URL : %AIX_DRL_APP_URL%

echo.
echo [1/8] Previewing hub upload payload...
call gcloud meta list-files-for-upload > upload-list.txt
if errorlevel 1 goto :fail_popd
for /f %%i in ('find /c /v "" ^< upload-list.txt') do set UPLOAD_COUNT=%%i
echo Upload file count: %UPLOAD_COUNT%

echo.
echo [2/8] Deploying RPS service if present...
if exist "%RPS_ROOT%\app.aix.yaml" (
  pushd "%RPS_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %RPS_ROOT%\app.aix.yaml not found
)

echo.
echo [3/8] Deploying Connect4 service if present...
if exist "%C4_ROOT%\app.aix.yaml" (
  pushd "%C4_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %C4_ROOT%\app.aix.yaml not found
)

echo.
echo [4/8] Deploying Euclidorithm service if present...
if exist "%EUCLID_ROOT%\app.aix.yaml" (
  pushd "%EUCLID_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %EUCLID_ROOT%\app.aix.yaml not found
)

echo.
echo [5/8] Deploying Polyfolds service if present...
if exist "%PF_ROOT%\app.aix.yaml" (
  pushd "%PF_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %PF_ROOT%\app.aix.yaml not found
)

echo.
echo [6/8] Deploying default App Engine service...
echo ^> gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [7/8] Deploying dispatch rules...
echo ^> gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [8/8] Verifying deployed services...
echo ^> gcloud app services list --project="%PROJECT_ID%"
call gcloud app services list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail_popd
echo.
echo ^> gcloud app versions list --project="%PROJECT_ID%"
call gcloud app versions list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail_popd

echo.
echo [OK] App Engine deploy finished.
popd >nul
endlocal
exit /b 0

:fail_popd
popd >nul

:fail
echo.
echo [ERROR] Deploy failed.
endlocal
exit /b 1

:fail_popd_all
popd >nul
goto :fail_popd
