@echo off
cd /d "%~dp0video-chat-editor"
start "" "http://localhost:4180"
"%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" backend\server.py
