@echo off
setlocal
call "%~dp0aix_cloud_env.bat"

echo.
echo ==== AIX Cloud Status ====
echo Project: %PROJECT_ID%
echo Region : %REGION%
echo SA     : %SA_EMAIL%
echo DRL URL: %AIX_DRL_APP_URL%

echo.
echo ^> gcloud auth list
gcloud auth list
if errorlevel 1 goto :fail
echo.
echo ^> gcloud config list
gcloud config list
if errorlevel 1 goto :fail
echo.
echo ^> gcloud projects describe "%PROJECT_ID%"
gcloud projects describe "%PROJECT_ID%"
if errorlevel 1 goto :fail
echo.
echo ^> gcloud billing projects describe "%PROJECT_ID%"
gcloud billing projects describe "%PROJECT_ID%"
if errorlevel 1 goto :fail
echo.
echo ^> gcloud services list --enabled --project="%PROJECT_ID%"
gcloud services list --enabled --project="%PROJECT_ID%"
if errorlevel 1 goto :fail
echo.
echo ^> gcloud iam service-accounts list --project="%PROJECT_ID%"
gcloud iam service-accounts list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail
echo.
echo ^> gcloud iam service-accounts keys list --iam-account="%SA_EMAIL%" --project="%PROJECT_ID%"
gcloud iam service-accounts keys list --iam-account="%SA_EMAIL%" --project="%PROJECT_ID%"
if errorlevel 1 goto :fail
echo.
echo ^> gcloud storage buckets list --project="%PROJECT_ID%" --format="table(name,location,locationType,storageClass)"
gcloud storage buckets list --project="%PROJECT_ID%" --format="table(name,location,locationType,storageClass)"
if errorlevel 1 goto :fail
echo.
echo ^> gcloud app describe --project="%PROJECT_ID%"
gcloud app describe --project="%PROJECT_ID%"
if errorlevel 1 goto :fail

echo.
echo ^> gcloud app services list --project="%PROJECT_ID%"
gcloud app services list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail

echo.
echo ^> gcloud app versions list --project="%PROJECT_ID%"
gcloud app versions list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail

echo.
echo ^> gcloud app dispatch-rules list --project="%PROJECT_ID%"
gcloud app dispatch-rules list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail

echo.
echo ^> gcloud secrets list --project="%PROJECT_ID%"
gcloud secrets list --project="%PROJECT_ID%"
if errorlevel 1 goto :fail

echo.
echo [OK] Status inspection finished.
endlocal
exit /b 0

:fail
echo.
echo [ERROR] One of the required gcloud commands failed.
endlocal
exit /b 1
