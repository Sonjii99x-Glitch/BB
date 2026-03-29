@echo off
set /p OPI_IP=Enter Orange Pi Server IP:
set /p PASSWORD=Enter OPI root password:

echo Copying files to Orange Pi...
pscp -r "%USERPROFILE%\Downloads\windows_client\*" root@%OPI_IP%:/root/pisonet/

echo Setting permissions...
plink root@%OPI_IP% -pw %PASSWORD% "chmod -R 755 /root/pisonet/"

echo Starting PisoNet service...
plink root@%OPI_IP% -pw %PASSWORD% "systemctl daemon-reload && systemctl start pisonet.service"

echo Installation complete.
pause