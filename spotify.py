import os
import subprocess
from dotenv import load_dotenv

class Spotify:

	def __init__(self):
		load_dotenv()
		self.clientId = os.getenv('SPOTIFY_CLIENT_ID')
		self.clientSecret = os.getenv('SPOTIFY_CLIENT_SECRET')
		self.deviceName = os.getenv('SPOTIFY_DEVICE')

	def login(self):
		# Note: this exits the app, you'll have to start the script again
		os.system(f'spotify auth login --client-id {self.clientId} --client-secret {self.clientSecret}')

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

	def playPlaylist(self, playlist):
		# The playlist can be passed as either the playlist ID,
		# or as the share link to the playlist
		if playlist.startswith('http'):
			self.playLink(playlist)
		else:
			os.system(f'spotify play --playlist spotify:playlist:{playlist} --shuffle on --repeat all')
		# Because '--shuffle on' does not seem to work as it should, we issue an extra command:
		os.system('spotify shuffle on')
		os.system('spotify next')

	def playLink(self, url):
		# The link can be any Spotify share link. Playlist, artist, etc.
		os.system(f'spotify play --uri {url} --shuffle on --repeat all')

	def playArtist(self, artist):
		# Basically a search query, but limited to artists
		os.system('spotify play --artist {artist} --shuffle on --repeat all')

	def playAlbum(self, album):
		# Search, limited to albums
		os.system('spotify play --album {album} --shuffle on --repeat all')

	def playSearch(self, query):
		# Unlimited search. Plays whatever matches best
		os.system('spotify play {query}')

	def pause(self):
		os.system('spotify pause')

	def resume(self):
		os.system('spotify play')
