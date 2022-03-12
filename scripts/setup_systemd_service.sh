#!/bin/bash

# Run this script to install a systemd service in "services/systemd/" onto the systenm
# Needed when updating the service scripts

# Append with service name
# ./scripts/setup_systemd_service.sh test.service


# Move and set permissions
sudo cp -rf services/systemd etc/systemd/system/$1
sudo chmod 644 etc/systemd/system/$1


# Configure systemd
sudo systemctl daemon-reload
sudo systemctl start $1
sudo systemctl enable $1


# Wait for startup and check status
sleep 5
sudo systemctl status $1
