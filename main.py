#!/bin/python3
import os
import re
import subprocess
import sys
import time
from dotenv import load_dotenv
from pickmeup import PickMeUp
from spotify import Spotify
from taghelper import getTags
from tag import Tag
from lights import Lights
from tts import TTS
from pydub import AudioSegment
from pydub.playback import play

class Chuckberry:

	AUDIO_RESPONSE_TTS = "tts"
	AUDIO_RESPONSE_NOTIFICATION = "notification"
	AUDIO_RESPONSE_NONE = "none"
	NOTIFICATION_STARTUP = 0
	NOTIFICATION_SUCCESS = 1
	NOTIFICATION_ERROR = 2

	def __init__(self):
		self.tags = {}
		self.spotify = Spotify()
		self.lastTag = None
		self.lastTimestamp = 0
		self.tts = TTS()
		# Load endpoints from .env
		load_dotenv()
		self.endpoint = os.getenv('ENDPOINT')
		self.enableLights = not os.getenv('DISABLE_LIGHTS') == "true"
		self.audioResponse = os.getenv('AUDIO_RESPONSE')
		# Load audio fragments (if needed)
		if self.audioResponse == "notification":
			self.sounds = [None, None, None]
			self.sounds[0] = AudioSegment.from_mp3("./assets/startup.mp3")
			self.sounds[1] = AudioSegment.from_mp3("./assets/success.mp3")
			self.sounds[2] = AudioSegment.from_mp3("./assets/error.mp3")
		# Connect to the Twinkly lights
		self.lights = Lights()
		if self.enableLights:
			self.lights.connect()

	def say(self, msg, type = -1):
		if self.audioResponse == Chuckberry.AUDIO_RESPONSE_TTS:
			self.tts.say(msg)
		elif self.audioResponse == Chuckberry.AUDIO_RESPONSE_NOTIFICATION:
			print(msg)
			if type >= 0:
				play(self.sounds[type])

	def loadConfig(self):
		print('Loading project configuration...')
		self.tags = getTags(self.endpoint)

	def pickUp(self, tagNumber):
		print(f'Tag {tagNumber} picked up')
		key = str(tagNumber)
		if key in self.tags:
			self.pickUpTag(self.tags[key])
		else:
			pass

	def pickUpTag(self, tag):
		if tag.action is not None:
			# Actions are handled when the tag is put back
			pass
		else:
			# Only pause if we picked up the tag that last started playing
			if tag.number == self.lastTag:
				self.spotify.pause()
				self.say('Playback paused', type = Chuckberry.NOTIFICATION_SUCCESS)
				self.lastTag = tag.number
				self.lastTimestamp = time.time()

	def putBack(self, tagNumber):
		print(f'Tag {tagNumber} put back')
		key = str(tagNumber)
		if key in self.tags:
			self.putBackTag(self.tags[key])
		else:
			self.lights.error()
			self.say(f'No playlist associated with tag {tagNumber}', type = Chuckberry.NOTIFICATION_ERROR)

	def putBackTag(self, tag):
		if tag.action is not None:
			self.handleAction(tag.action)
		else:
			if tag.color is not None:
				self.lights.blink(Lights.PICKUP_COLOR, tag.color)
			else:
				self.lights.blink(Lights.PICKUP_COLOR)
			type = tag.getTypeName()
			if tag.number == self.lastTag:
				# Resuming what was picked up earlier
				self.spotify.resume()
				self.say(f'Resuming {type} {tag.playlist_name}')
			elif tag.type == Tag.TYPE_LOCAL_PATH:
				self.say('Sorry, playing local audio files is not supported yet')
			elif tag.type == Tag.TYPE_URL:
				self.say('Sorry, playing music from a URL is not supported yet')
			elif tag.type == Tag.TYPE_SPOTIFY_PLAYLIST:
				self.spotify.playPlaylist(tag.url)
				print(f'Starting {tag.type} {tag.url}')
				self.say(f'Tag detected. Playing {tag.playlist_name}')
			elif tag.type == Tag.TYPE_SPOTIFY_ARTIST:
				self.spotify.playArtist(tag.url)
				print(f'Starting {tag.type} {tag.url}')
				self.say(f'Tag detected. Playing {tag.playlist_name}')
			elif tag.type == Tag.TYPE_SPOTIFY_ALBUM:
				self.spotify.playAlbum(tag.url)
				print(f'Starting {tag.type} {tag.url}')
				self.say(f'Tag detected. Playing {tag.playlist_name}')
			elif tag.type == Tag.TYPE_SPOTIFY_SEARCH:
				self.spotify.playSearch(tag.url)
				print(f'Starting {tag.type} {tag.url}')
				self.say(f'Tag detected. Playing {tag.playlist_name}')
			self.lastTag = tag.number
			self.lastTimestamp = time.time()

	def handleAction(self, action):
		"""
		Supported actions:
		  refresh - Refreshes the configuration
		  shutdown - shutdown the Pi
		"""
		if action == "refresh":
			self.lights.blink(Lights.REFRESH_COLOR)
			self.say('Refreshing configuration', type = Chuckberry.NOTIFICATION_SUCCESS)
			self.loadConfig()
			if self.spotify.selectDevice():
				self.say('Done', type = Chuckberry.NOTIFICATION_STARTUP)
			else:
				self.say('Please start Spotify playback on one of your devices')
		elif action == "next":
			self.lights.blink(Lights.DEFAULT_COLOR)
			self.say('Next!', type = Chuckberry.NOTIFICATION_SUCCESS)
			self.spotify.selectDevice()
			self.spotify.next()
		elif action == "shutdown":
			if isRoot():
				self.lights.blink(Lights.SHUTDOWN_COLOR)
				self.say('Shutting down...', type = Chuckberry.NOTIFICATION_SUCCESS)
				os.system("halt")
			else:
				self.say('Cannot shut down, not enough permission', type = Chuckberry.NOTIFICATION_ERROR)
				self.lights.error()
		else:
			print(f'Unknown command: {action}')
			self.lights.error()


def isRoot():
	return os.geteuid() == 0

def main():
	# Load configuration from JSON
	chuck = Chuckberry()
	chuck.say("Loading...")
	chuck.loadConfig()
	chuck.lights.loading()
	# Connect to USB device
	print('Connecting to smart shelf...')
	pu = PickMeUp(pickUpCallback = chuck.pickUp, putBackCallback = chuck.putBack, silent = False)
	pu.connect()
	pu.setGainLevel(4)
	pu.setLEDBehaviour(1)
	pu.setGhostFilter(10)
	# Select a device to play one. Assumes we're logged in to spotify-cli, and that the name of the device is in the .env
	print('Connecting to Spotify...')
	if chuck.spotify.selectDevice():
		chuck.say("Ready", type = Chuckberry.NOTIFICATION_STARTUP)
		chuck.lights.ready()
	else:
		chuck.say('Please start Spotify playback on one of your devices.', type = Chuckberry.NOTIFICATION_ERROR)
		chuck.lights.error()
	# Start main loop
	if pu.startThread():
		pu.scan()
		print('Put a tag on the sensor to get a response')
		while 1:
			pass
	else:
		print('Unable to connect')

if __name__ == '__main__':
	# To support the shutdown command and to
	# start the Raspotify service if it isn't running,
	# you should be running this script as root.
	if not isRoot():
		print('If this script is not run as root, it can\'t shutdown the Pi')
	main()
