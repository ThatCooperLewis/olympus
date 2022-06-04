#!/bin/bash

echo "Starting monitor service shell script..."

# OrangePi is slow as fuck to boot up, wait for internet connection, otherwise `git pull` will fail
sleep 30

cd ~/olympus
git pull

source venv/bin/activate
source .env.production

python3.10 -m pip install -r requirements-no-cuda.txt
python3.10 services_manager.py monitor