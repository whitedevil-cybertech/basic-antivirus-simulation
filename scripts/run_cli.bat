@echo off
REM Reliable CLI launcher (no PATH setup needed)
setlocal
cd /d "%~dp0\.."

py -m basic_antivirus_simulation.cli %*

endlocal
