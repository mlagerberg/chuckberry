import os
import subprocess
from dotenv import load_dotenv

class Spotify:

	def __init__(self):
		load_dotenv()
		self.clientId = os.getenv('SPOTIFY_CLIENT_ID')
		self.clientSecret = os.getenv('SPOTIFY_CLIENT_SECRET')
		self.deviceName = os.getenv('SPOTIFY_DEVICE')

	def exec(self, command):
		full_command = f'spotify {command}'
		print(f'executing: {full_command}')
		os.system(full_command)

	def login(self):
		# Note: this exits the app, you'll have to start the script again
		self.exec(f'auth login --client-id {self.clientId} --client-secret {self.clientSecret}')

	def selectDevice(self):
		"""
		Executes the command `spotify devices --switch-to <name>`.
		Does not wait for user input but fails if the device
		is not found. Returns False in that case, True otherwise.
		"""
		# In this case, we don't use os.system, because we don't want to wait for user input and want
		# to check the return code instead
		p = subprocess.run(["spotify", "device", "--switch-to", self.deviceName], stdin=subprocess.DEVNULL)
		return p.returncode == 0

	def next(self):
		self.exec('next')

	def playPlaylist(self, playlist):
		# The playlist can be passed as either the playlist ID,
		# or as the share link to the playlist
		if playlist.startswith('http'):
			self.playLink(playlist)
		else:
			self.exec(f'play --playlist spotify:playlist:{playlist} --shuffle on --repeat all')

	def playLink(self, url):
		# The link can be any Spotify share link. Playlist, artist, etc.
		self.exec(f'play --uri {url} --shuffle on --repeat all')

	def playAlbum(self, album):
		# Search, limited to albums
		self.exec(f'play --album {album} --shuffle on --repeat all')

	def playSearch(self, query):
		# Unlimited search. Plays whatever matches best
		self.exec(f'play {query}')

	def pause(self):
		self.exec('pause')

	def resume(self):
		self.exec('play')
