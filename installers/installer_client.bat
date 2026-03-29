@echo off
set OPI_IP=%1
set PASSWORD=%2

echo Copying client files...
xcopy "%~dp0..\windows_client\*" "C:\Program Files\PisoNetClient\" /E /I /Y

echo Setting up client...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v PisoNetClient /t REG_SZ /d "python \"C:\Program Files\PisoNetClient\client.py\"" /f

echo Client installation complete.