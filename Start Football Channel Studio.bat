@echo off
cd /d "%~dp0channel-studio"
set PORT=4174
start "" "http://localhost:4174"
"%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" server.js
