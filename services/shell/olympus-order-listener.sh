#!/bin/bash

cd /home/cooper/olympus/ && git pull && source venv/bin/activate && python3.10 -m pip install -r requirements-no-cuda.txt && python3.10 services_manager.py orders