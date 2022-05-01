#!/bin/bash

# Install Linux packages
sudo apt install python3-pip python3-venv libpulse0 espeak
# This helps install dependencies for libpulse:
sudo apt --fix-broken install

# Install Raspotify
wget https://dtcooper.github.io/raspotify/raspotify-latest_arm64.deb
sudo dpkg -i raspotify-latest_arm64.deb
rm -f raspotify-latest_arm64.deb
sudo systemctl enable raspotify

# Install Python modules
sudo pip3 install -r requirements.txt

echo <<EOF
Done.
Edit .env and then start the ChuckBerry by running:
./main.py
EOF
