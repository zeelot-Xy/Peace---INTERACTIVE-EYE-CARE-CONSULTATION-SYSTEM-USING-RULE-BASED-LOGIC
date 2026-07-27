@echo off
echo This creates a safety backup and resets all local application accounts and consultations.
set /p CONFIRM=Type RESET to continue: 
if /I not "%CONFIRM%"=="RESET" (
  echo Reset cancelled.
  pause
  exit /b 1
)
"%~dp0EyeCareConsultation.exe" reset-demo-data --confirm
pause
