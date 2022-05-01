
# Installation

Assuming Rasbian and Python 3.7 or up.

The easiest way to install is to run `./setup.sh`. This will install
several Linux packages and Python modules. Below is the full list of things to
install if you want to do it manually.


### Install requirements

The required packages are these:

```bash
sudo apt install python3-pip python3-venv
pip3 install -r requirements.txt
```

If you want to run the script as root, so you can shut down the Pi
using a tag, we recommend using a virtual environment:

```bash
sudo apt install python3-pip python3-venv
python3 -m venv cbenv
source cbenv/bin/activate
sudo pip3 install -r requirements.txt
```

### Start Spotify

The app works as a remote to control a Spotify connected speaker, but it can
also act as such a connected speaker. Spotify needs to be playing on a device
for the script to be able to control it. So, play Spotify music on a device
and make sure it is listed in the 'devices' part. E.g., playing on your phone
won't cut it, but using your phone to play on a Chromecast device or smart
speaker will. Note the name of the device.

Next, create a `.env` file by copying `.sample.env` and filling in the blanks.
Enter the name of the device that is playing in the `SPOTIFY_DEVICE=` part.
It does not have to be exact as long as it is a good match.

### Spotify-cli

Log in to Spotify-cli using this command. This will give you a link you should
open in a browser, and the token received after login should be fed back into
the terminal.

```bash
# Make sure to do this in the virtual environment, if you chose to use that
source cbenv/bin/activate
spotify auth login
```

### Raspotify

Turns this device into a Spotify Connect host. Not necessary to run this app,
you can playbak on another device, but it does turn the Pi into a one-stop
solution. Note: requires Spotify Premium. Playback on a Chromecast or bluetooth
speaker does not!

```bash
wget https://dtcooper.github.io/raspotify/raspotify-latest_arm64.deb
sudo apt install libpulse0
sudo apt --fix-broken install
sudo dpkg -i raspotify-latest_arm64.deb
rm -f raspotify-latest_arm64.deb
sudo systemctl enable raspotify
```

Change the name and settings of the device if you want, as long as you also
update it in your `.env` file:

```bash
sudo nano /etc/raspotify/conf
```

You can control this service like a regular systemd service:

```bash
sudo systemctl restart raspotify
```

More documentation on Raspotify [can be found here][raspotify].

### Serial comms

Optional: if the app does not connect to the USB device automatically, check if
it is connected to the correct serial port. Discover the connected USB port by
running:

```bash
dmesg | grep tty
```

Look for something like `ttyUSB0`. Update `pickmeup.py` if needed.

### Text to Speech

We use the system's built-in TTS. On Raspbian, that is `espeak`. It is not
the best, but it works. You can disable it by editing the `.env` file.

```bash
sudo apt-get install espeak
pip3 install pyttsx3
```

[spotify]: https://developer.spotify.com/dashboard
[raspotify]: https://dtcooper.github.io/raspotify/
