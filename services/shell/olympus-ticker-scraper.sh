#!/bin/bash

echo "Starting ticker service shell script..."

cd ~/olympus
git pull

source venv/bin/activate
source .env.production

python3.10 -m pip install -r requirements-cudaless.txt
python3.10 services_manager.py scraper