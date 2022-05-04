
class TagFormatError(Exception):
	pass

class Tag:

	TYPE_SPOTIFY_PLAYLIST = "spotify_playlist"
	TYPE_SPOTIFY_ALBUM = "spotify_album"
	TYPE_SPOTIFY_SEARCH = "spotify_search"
	TYPE_LOCAL_PATH = "filepath"
	TYPE_URL = "url"

	def __init__(self, tagValue):
		self.number = -1
		self.color = None
		self.tag_name = None
		self.playlist_name = None
		self.type = Tag.TYPE_SPOTIFY_PLAYLIST
		if isinstance(tagValue, str):
			self.url = str
			self.action = None
		else:
			try:
				self.number = tagValue["tag_number"]
			except:
				raise TagFormatError("No tag_number defined for this tag")
			# Tags can either have an action or a link associated:
			if "action" in tagValue:
				self.action = tagValue["action"]
				self.url = None
			elif "link" in tagValue:
				self.url = tagValue["link"]
				self.action = None
			else:
				raise TagFormatError("No link or action defined for this tag")
			# In case of a link, it can be a path to a file, or a spotify playlist, or a ...
			# Defaults to spotify playlist if no type is set
			if "type" in tagValue:
				self.type = tagValue["type"]
			# Optional: tag name and playlist name
			# The tag name refers to the object the NFC tag is stuck to,
			# while the playlist name refers to the link (Spotify playlist, artist, etc.)
			if "tag_name" in tagValue:
				self.tag_name = tagValue["tag_name"]
			if "playlist_name" in tagValue:
				self.playlist_name = tagValue["playlist_name"]
			# Possibly also a color action (for the Twinkly lights):
			if "color" in tagValue:
				self.color = tagValue["color"]

	def getTypeName(self):
		"""
		Translates the `type` to something human-readable
		(or robot-sayable)
		"""
		if self.type == Tag.TYPE_SPOTIFY_PLAYLIST:
			return "playlist"
		elif self.type == Tag.TYPE_SPOTIFY_ALBUM:
			return "album"
		elif self.type == Tag.TYPE_SPOTIFY_SEARCH:
			# Let's keep it generic. We'll play music, we won't play 'a search query':
			return "music"
		elif self.type == Tag.TYPE_LOCAL_PATH:
			return "song"
		elif self.type == Tag.TYPE_URL:
			return "stream"
		else:
			return "tag"

	def print(self):
		"""
		Prints (some) properties of this tag in human readable
		form to the console
		"""
		tagName = str(self.number)
		if self.tag_name is not None:
			tagName = f'{tagName} ({self.tag_name})'
		if self.action is not None:
			print(f'Tag {tagName} = action: {self.action}')
		else:
			playlist = self.url
			if self.playlist_name is not None:
				playlist = f'{self.playlist_name} (url: {playlist})'
			print(f'Tag {tagName} = playlist: {playlist}')
