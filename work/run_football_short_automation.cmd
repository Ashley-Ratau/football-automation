@echo off
setlocal

for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "PYTHON=C:\Users\Wendy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "SCRIPT=%ROOT%\work\football_short_automation.py"
set "LOGDIR=%ROOT%\work\automation_state\logs"

if not exist "%PYTHON%" (
  echo Bundled Python runtime not found: %PYTHON%
  exit /b 1
)

if not exist "%SCRIPT%" (
  echo Automation script not found: %SCRIPT%
  exit /b 1
)

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "STAMP=%%i"

set "STDOUT=%LOGDIR%\%STAMP%.stdout.log"
set "STDERR=%LOGDIR%\%STAMP%.stderr.log"

"%PYTHON%" "%SCRIPT%" --run-once 1>"%STDOUT%" 2>"%STDERR%"
if errorlevel 1 (
  echo Football automation failed. See logs: %STDOUT% and %STDERR%
  exit /b 1
)

echo Football automation completed successfully.
