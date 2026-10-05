@echo off
cd /d "%~dp0"
"%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" work\generate_elevenlabs_voiceover.py generate --project %*
