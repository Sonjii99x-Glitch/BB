#!/bin/bash

# SD Image Builder for PisoNet
# Requires Armbian image as base

BASE_IMAGE="Armbian_26.2.1_Trixie_Minimal_orangepione.img"
OUTPUT_IMAGE="pisonet_ready.img"

# Copy base image
cp $BASE_IMAGE $OUTPUT_IMAGE

# Mount and customize (simplified, in real use use losetup or similar)
# For demo, assume mounted at /mnt

echo "Copying PisoNet files to image..."
cp -r /workspaces/BB/pisonet_server/* /mnt/root/pisonet/
cp -r /workspaces/BB/admin_dashboard/* /mnt/root/admin_dashboard/

echo "Setting up services..."
# Enable services in image

echo "Image ready: $OUTPUT_IMAGE"