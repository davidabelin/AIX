@echo off
setlocal

if /i "%~1"=="--help" goto :help
if /i "%~1"=="-h" goto :help
if /i "%~1"=="/?" goto :help

set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%aix_cloud_env.bat"
if errorlevel 1 goto :fail

pushd "%SCRIPT_DIR%" >nul 2>&1
if errorlevel 1 goto :fail

for %%I in ("%CD%\..") do set "AIX_ROOT=%%~fI"
set "RPS_ROOT=%AIX_ROOT%\..\rps"
set "C4_ROOT=%AIX_ROOT%\..\c4"
set "DOUBLEDIGITS_ROOT=%AIX_ROOT%\..\dd"
set "EUCLIDYNE_ROOT=%AIX_ROOT%\..\geometry\euclidyne"
set "PF_ROOT=%AIX_ROOT%\..\pf"

echo.
echo ==== AIX Deploy Entry Point ====
echo Project : %PROJECT_ID%
echo Region  : %REGION%
echo Service : %SERVICE_NAME%
echo.
echo This deploy uploads the current local working trees for AIX-managed services
echo and sibling lab repos still deployed with AIX. Clue is intentionally excluded;
echo deploy Clue separately from ..\clue\deploy_clue.bat.
echo Uncommitted local edits are part of the payload; Git commits are not required
echo for the deployed code to change.
echo Assumes gc.bat or an equivalent gcloud auth/config setup has already run.

call :check_tool gcloud
if errorlevel 1 goto :fail_popd
call :check_tool git
if errorlevel 1 goto :fail_popd

echo.
echo [1/2] Deployment scope preview...
call :show_repo_state "AIX hub" "%AIX_ROOT%" "app.yaml"
call :show_repo_state "RPS" "%RPS_ROOT%" "app.aix.yaml"
call :show_repo_state "Connect4" "%C4_ROOT%" "app.aix.yaml"
call :show_repo_state "Double-digits" "%DOUBLEDIGITS_ROOT%" "app.aix.yaml"
call :show_repo_state "Euclidyne" "%EUCLIDYNE_ROOT%" "app.aix.yaml"
call :show_repo_state "Polyfolds" "%PF_ROOT%" "app.aix.yaml"

echo.
echo [2/2] Running cloud deploy...
call "%SCRIPT_DIR%aix_cloud_deploy.bat"
if errorlevel 1 goto :fail_popd

echo.
echo [OK] scripts\deploy completed successfully.
popd >nul
endlocal
exit /b 0

:help
echo Usage: scripts\deploy
echo.
echo Runs the standard multi-service App Engine deployment for AIX-managed services.
echo Assumes gc.bat has already selected the service account and gcloud project.
echo Clue is not included; deploy it separately with ..\clue\deploy_clue.bat.
echo.
echo Deploy behavior:
echo   - uploads current local filesystem contents, including uncommitted edits
echo   - previews which repos and manifests are in scope
echo   - delegates the actual deploy to scripts\aix_cloud_deploy.bat
echo.
endlocal
exit /b 0

:check_tool
where "%~1" >nul 2>&1
if errorlevel 1 (
  echo.
  echo [ERROR] Required tool not found on PATH: %~1
  exit /b 1
)
exit /b 0

:show_repo_state
set "LABEL=%~1"
set "ROOT=%~2"
set "MANIFEST=%~3"

echo %LABEL%
echo   Path     : %ROOT%

if not exist "%ROOT%" (
  echo   Status   : [skip] repo path not found
  exit /b 0
)

if exist "%ROOT%\%MANIFEST%" (
  echo   Manifest : %MANIFEST%
  echo   Deploy   : included
) else (
  echo   Manifest : [missing] %MANIFEST%
  echo   Deploy   : skipped
  exit /b 0
)

if not exist "%ROOT%\.git" (
  echo   Git      : unavailable
  exit /b 0
)

set "STATUS_FILE=%TEMP%\aix_deploy_status_%RANDOM%_%RANDOM%.txt"
pushd "%ROOT%" >nul 2>&1
if errorlevel 1 (
  echo   Git      : repo unreadable
  exit /b 0
)

git status --short --untracked-files=all > "%STATUS_FILE%" 2>nul
if errorlevel 1 (
  echo   Git      : status unavailable
) else (
  for %%A in ("%STATUS_FILE%") do (
    if %%~zA EQU 0 (
      echo   Git      : clean
    ) else (
      echo   Git      : dirty; deploy uses current local files
      for /f "usebackq delims=" %%L in ("%STATUS_FILE%") do echo     %%L
    )
  )
)

del "%STATUS_FILE%" >nul 2>&1
popd >nul
exit /b 0

:fail_popd
popd >nul

:fail
echo.
echo [ERROR] scripts\deploy failed.
endlocal
exit /b 1
