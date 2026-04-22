@echo off
REM Reliable GUI launcher (no PATH setup needed)
setlocal
cd /d "%~dp0\.."

py -m basic_antivirus_simulation.gui_app

endlocal
