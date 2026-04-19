#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y build-essential gdb make python3 python3-venv python3-pip

echo "Ubuntu C OS coding environment dependencies installed."
