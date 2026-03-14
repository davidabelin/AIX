@echo off
setlocal
call "%~dp0aix_cloud_env.bat"
pushd "%~dp0" >nul 2>&1
if errorlevel 1 goto :fail

echo.
echo ==== AIX App Engine Deploy ====
echo Project : %PROJECT_ID%
echo Region  : %REGION%
echo Service : %SERVICE_NAME%
echo DRL URL : %AIX_DRL_APP_URL%

echo.
echo [1/4] Previewing upload payload...
call gcloud meta list-files-for-upload > upload-list.txt
if errorlevel 1 goto :fail_popd
for /f %%i in ('find /c /v "" ^< upload-list.txt') do set UPLOAD_COUNT=%%i
echo Upload file count: %UPLOAD_COUNT%

echo.
echo [2/4] Deploying default App Engine service...
echo ^> gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy app.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [3/4] Deploying dispatch rules...
echo ^> gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
call gcloud app deploy dispatch.yaml --project="%PROJECT_ID%" --quiet
if errorlevel 1 goto :fail_popd

echo.
echo [4/4] Verifying deployed services...
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
