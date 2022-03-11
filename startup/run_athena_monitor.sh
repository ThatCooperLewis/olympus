#!/bin/bash

# Include path to Olympus in command
# ./run_athena.sh <path_to_repo>

cd $1
source venv/bin/activate
python3.10 athena_monitor.py &
cd -