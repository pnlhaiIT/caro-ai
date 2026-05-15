#!/bin/bash

set -e

# venv hoặc .venv
if  [ -d ".venv" ] || [ -d "venv" ]; then
    echo "virtual env existed"
else
    python3 -m venv .venv 
    source .venv/bin/activate 
fi 

pip install -r engine/requirements.txt
python3 engine/app.py 
