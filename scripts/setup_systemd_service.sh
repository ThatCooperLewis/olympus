#!/bin/bash

# Run this script to install a systemd service in "services/systemd/" onto the systenm
# Needed when updating the service scripts

# Append with service name
# ./scripts/setup_systemd_service.sh test.service


echo "Moving service to /etc/systemd/system..."
sudo cp -rf services/systemd/$1 /etc/systemd/system/$1
sudo chmod 644 /etc/systemd/system/$1

echo "Stopping old service..."
sudo systemctl stop $1

echo "Calling daemon-reload..."
sudo systemctl daemon-reload

echo "Starting service..."
sudo systemctl start $1
sudo systemctl enable $1

echo "Waiting for initialization..."
sleep 5
sudo systemctl status $1

echo "Done. New service started & enabled."