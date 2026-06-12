@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: commit-push.bat "Commit message" ["Optional body"]
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\commit-push.ps1" %*
exit /b %ERRORLEVEL%
