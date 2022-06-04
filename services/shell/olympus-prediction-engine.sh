#!/bin/bash

echo "Starting prediction service shell script..."

cd ~/olympus
git pull

source venv/bin/activate
source .env.production

python3.10 -m pip install -r requirements.txt
python3.10 services_manager_cuda.py prediction