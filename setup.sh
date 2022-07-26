#!/bin/bash

# Install Linux packages
sudo apt install python3-pip python3-venv libpulse0 espeak ffmpeg libavcodec-extra
# This helps install dependencies for libpulse:
sudo apt --fix-broken install

# Install Raspotify
wget https://dtcooper.github.io/raspotify/raspotify-latest_arm64.deb
sudo dpkg -i raspotify-latest_arm64.deb
rm -f raspotify-latest_arm64.deb
sudo systemctl enable raspotify

# Install Python modules
sudo pip3 install -r requirements.txt

# Workaround for a Spotify connection issue in certain countries:
echo <<EOF >> /etc/hosts
127.0.0.1 	apresolve.spotify.com
104.199.65.124 	ap-gew4.spotify.com
EOF

echo <<EOF
Done.
Edit .env and then start the ChuckBerry by running:
./main.py
EOF
