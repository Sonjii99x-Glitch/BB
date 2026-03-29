@echo off
cd /d "%~dp0"
set /p OPI_IP=Enter Orange Pi Server IP:
set /p PASSWORD=Enter OPI root password:

echo Installing PisoNet Server...
call installer_server.bat %OPI_IP% %PASSWORD%

echo Installing Windows Client...
call installer_client.bat %OPI_IP% %PASSWORD%

echo Installing Admin Dashboard...
call installer_admin.bat %OPI_IP% %PASSWORD%

echo All installations complete.
pause