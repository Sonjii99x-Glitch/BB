@echo off
set /p OPI_IP=Enter Orange Pi Server IP:
set /p PASSWORD=Enter OPI root password:

echo Installing PisoNet Server...
call installers\installer_server.bat %OPI_IP% %PASSWORD%

echo Installing Windows Client...
call installers\installer_client.bat %OPI_IP% %PASSWORD%

echo Installing Admin Dashboard...
call installers\installer_admin.bat %OPI_IP% %PASSWORD%

echo All installations complete.
pause