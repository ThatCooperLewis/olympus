#!/bin/bash

# Run this script to install a systemd service in "services/systemd/" onto the systenm
# Needed when updating the service scripts

# Append with service name
# ./scripts/setup_systemd_service.sh test.service


# Move and set permissions
echo "Moving service to /etc/systemd/system..."
sudo cp -rf services/systemd etc/systemd/systemd/$1
sudo chmod 644 etc/systemd/systemd/$1

echo "Stopping old service..."
sudo systemctl stop $1

# Configure systemd
echo "Configuring systemd..."
sudo systemctl daemon-reload
sudo systemctl start $1
sudo systemctl enable $1


echo "Waiting for initialization..."
sleep 5
sudo systemctl status $1
