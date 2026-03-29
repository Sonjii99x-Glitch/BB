# PisoNet Offline LAN System

## Overview
PisoNet is a coin-operated PC time system for local networks. It consists of an Orange Pi server, Windows client applications, and an admin dashboard.

## Components
- **Orange Pi Server**: Handles coin detection, session management, user accounts.
- **Windows Clients**: Lockscreen apps that require coins to unlock.
- **Admin Dashboard**: Web interface for management.
- **Installers**: One-click BAT files for deployment.
- **SD Image Builder**: Creates ready-to-flash images for Orange Pi.

## Prerequisites
- Windows PC with PuTTY installed (for pscp and plink commands).
- Orange Pi with Armbian flashed and booted.
- DHCP IP noted for OPI.

## Deployment Instructions

### 1. Prepare Orange Pi
- Flash Armbian 26.2.1 Trixie Minimal to SD card.
- Boot Orange Pi, connect to LAN (DHCP IP).
- Note the IP address.

### 2. Run Master Installer
- Download all files to your Windows PC.
- Run `installers/master_installer.bat`.
- Enter OPI IP and root password when prompted.
- This will install server, client, and admin components.

### 3. Alternative: Manual Installation
- For server: Copy `pisonet_server/` to `/root/pisonet/` on OPI, run `install_server.sh`.
- For client: Copy `windows_client/` to `C:\Program Files\PisoNetClient\`, run as admin.
- For admin: Copy `admin_dashboard/` to `/root/admin_dashboard/` on OPI, run `python3 app.py`.

### 4. SD Image
- Run `sd_image_builder/build_image.sh` on a Linux machine with base Armbian image.
- Flash the resulting `pisonet_ready.img` to SD card.

## Configuration
- Edit `settings.json` for branding and coin value.
- Users are stored in `users.json` on server.

## Usage
- Clients show lockscreen, insert coin to start session.
- Admin panel (F10) for management.
- Dashboard at `http://opi_ip:8080`.

## Notes
- Ensure OPi.GPIO is installed for GPIO control.
- Compile `client.py` to `client.exe` using PyInstaller for Windows.
- System supports unlimited clients in full mode, trial limited to 2.
