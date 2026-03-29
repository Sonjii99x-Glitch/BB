@echo off
set OPI_IP=%1
set PASSWORD=%2

echo Copying server files to Orange Pi...
pscp -r "%~dp0..\pisonet_server\*" root@%OPI_IP%:/root/pisonet/

echo Running server installer...
plink root@%OPI_IP% -pw %PASSWORD% "chmod +x /root/pisonet/install_server.sh && /root/pisonet/install_server.sh"

echo Server installation complete.