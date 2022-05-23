#!/bin/bash

# install dependencies
command -v pip3 >/dev/null 2>&1 || python3 <(curl -s https://bootstrap.pypa.io/get-pip.py)
pip3 install prometheus_client

touch ~/done
