#!/bin/bash/

WORK_DIR=$(dirname "${BASH_SOURCE[0]}")

python3 -m pip install opencensus
python3 -m pip install opencensus-ext-azure

nohup python3 $WORK_DIR/azinsights_main.py
