@echo off
setlocal
call "%~dp0aix_cloud_env.bat"
pushd "%~dp0" >nul 2>&1
if errorlevel 1 goto :fail
set "AIX_ROOT=%CD%"
set "RPS_ROOT=%AIX_ROOT%\..\rps"
set "C4_ROOT=%AIX_ROOT%\..\c4"
set "CLUE_ROOT=%AIX_ROOT%\..\clue"
set "DOUBLEDIGITS_ROOT=%AIX_ROOT%\..\dd"
set "EUCLIDYNE_ROOT=%AIX_ROOT%\..\geometry\euclidyne"
set "PF_ROOT=%AIX_ROOT%\..\pf"

echo.
echo ==== AIX App Engine Deploy ====
echo Project : %PROJECT_ID%
echo Region  : %REGION%
echo Hub     : %SERVICE_NAME%
echo DRL URL : %AIX_DRL_APP_URL%

echo.
echo [1/10] Previewing hub upload payload...
call gcloud meta list-files-for-upload > upload-list.txt
if errorlevel 1 goto :fail_popd
for /f %%i in ('find /c /v "" ^< upload-list.txt') do set UPLOAD_COUNT=%%i
echo Upload file count: %UPLOAD_COUNT%

echo.
echo [2/10] Deploying RPS service if present...
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
echo [3/10] Deploying Connect4 service if present...
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
echo [4/10] Deploying Clue service if present...
if exist "%CLUE_ROOT%\app.aix.yaml" (
  pushd "%CLUE_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %CLUE_ROOT%\app.aix.yaml not found
)

echo.
echo [5/10] Deploying Double-digits service if present...
if exist "%DOUBLEDIGITS_ROOT%\app.aix.yaml" (
  pushd "%DOUBLEDIGITS_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %DOUBLEDIGITS_ROOT%\app.aix.yaml not found
)

echo.
echo [6/10] Deploying Euclidyne service if present...
if exist "%EUCLIDYNE_ROOT%\app.aix.yaml" (
  pushd "%EUCLIDYNE_ROOT%" >nul
  echo ^> gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  call gcloud app deploy app.aix.yaml --project="%PROJECT_ID%" --quiet
  if errorlevel 1 goto :fail_popd_all
  popd >nul
) else (
  echo [SKIP] %EUCLIDYNE_ROOT%\app.aix.yaml not found
)

echo.
echo [7/10] Deploying Polyfolds service if present...
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
echo [8/10] Deploying default App Engine service...
echo ^> gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [9/10] Deploying dispatch rules...
echo ^> gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [10/10] Verifying deployed services...
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
