#!/bin/bash

echo "Starting order service shell script..."

cd ~/cicd
git pull

source venv/bin/activate
source .env.production

python3.10 -m pip install -r requirements.txt
python3.10 services_manager_cuda.py integration