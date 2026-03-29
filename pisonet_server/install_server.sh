#!/bin/bash

# PisoNet Server Installer for Orange Pi One
# Run as root

echo "Installing dependencies..."
apt update
echo "Installing Python dependencies..."
pip3 install --break-system-packages -r /root/pisonet/requirements.txt

echo "Creating directories..."
mkdir -p /root/pisonet/api
mkdir -p /root/pisonet/scripts
mkdir -p /root/pisonet/data
mkdir -p /root/pisonet/services

echo "Copying files..."
# Assume files are copied via SCP or manually
# cp /path/to/files/* /root/pisonet/

echo "Setting permissions..."
chmod +x /root/pisonet/api/app.py
chmod 755 /root/pisonet/data/*.json

echo "Installing systemd service..."
cp /root/pisonet/services/pisonet.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pisonet.service
systemctl start pisonet.service

echo "Installation complete. Server running on port 5000."