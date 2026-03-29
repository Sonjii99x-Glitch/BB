@echo off
set OPI_IP=%1
set PASSWORD=%2

echo Copying admin files to Orange Pi...
plink root@%OPI_IP% -pw %PASSWORD% "mkdir -p /root/admin_dashboard"
pscp -r "%~dp0..\admin_dashboard\*" root@%OPI_IP%:/root/admin_dashboard/

echo Installing admin dependencies...
plink root@%OPI_IP% -pw %PASSWORD% "pip3 install --break-system-packages -r /root/admin_dashboard/requirements.txt"

echo Starting admin dashboard...
plink root@%OPI_IP% -pw %PASSWORD% "cd /root/admin_dashboard && python3 app.py &"

echo Admin installation complete.