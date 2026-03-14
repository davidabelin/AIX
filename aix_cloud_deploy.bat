@echo off
setlocal
call "%~dp0aix_cloud_env.bat"
pushd "%~dp0" >nul 2>&1
if errorlevel 1 goto :fail
set "AIX_ROOT=%CD%"
set "RPS_ROOT=%AIX_ROOT%\..\rps"
set "C4_ROOT=%AIX_ROOT%\..\c4"
set "EUCLID_ROOT=%AIX_ROOT%\..\geometry\euclidorithm"

echo.
echo ==== AIX App Engine Deploy ====
echo Project : %PROJECT_ID%
echo Region  : %REGION%
echo Hub     : %SERVICE_NAME%
echo DRL URL : %AIX_DRL_APP_URL%

echo.
echo [1/7] Previewing hub upload payload...
call gcloud meta list-files-for-upload > upload-list.txt
if errorlevel 1 goto :fail_popd
for /f %%i in ('find /c /v "" ^< upload-list.txt') do set UPLOAD_COUNT=%%i
echo Upload file count: %UPLOAD_COUNT%

echo.
echo [2/7] Deploying RPS service if present...
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
echo [3/7] Deploying Connect4 service if present...
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
echo [4/7] Deploying Euclidorithm service if present...
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
echo [5/7] Deploying default App Engine service...
echo ^> gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [6/7] Deploying dispatch rules...
echo ^> gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [7/7] Verifying deployed services...
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
