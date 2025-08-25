#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/pi/church"
DEVICE_DIR="$REPO_DIR/device"

sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev git
sudo raspi-config nonint do_spi 0

pip3 install spidev requests python-dotenv

sudo cp "$DEVICE_DIR/temp-agent.service" /etc/systemd/system/temp-agent.service
sudo systemctl daemon-reload
sudo systemctl enable temp-agent.service
sudo systemctl restart temp-agent.service
sudo systemctl status temp-agent.service --no-pager
