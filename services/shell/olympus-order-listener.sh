#!/bin/bash

echo "Starting order service shell script..."

cd ~/olympus
git pull

source venv/bin/activate
source .env.production

python3.10 -m pip install -r requirements-no-cuda.txt
python3.10 services_manager.py orders