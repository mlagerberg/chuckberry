import time
import threading
import xled
from color import hexToRGB

class Lights:

	DEFAULT_COLOR = "eb6734"
	PICKUP_COLOR = "fca503"
	PUTBACK_COLOR = "fca503"
	SHUTDOWN_COLOR ="b80f0f"
	REFRESH_COLOR = "0978d9"
	BLINK_OFF_COLOR = "000000"
	ERROR_COLOR = "ff0000"
	LOADING_COLOR = "a0a0a0"

	def __init__(self):
		self.device = None
		self.lastColor = Lights.DEFAULT_COLOR
		# I have no self control
		self.control = None
		self.high = None

	def connect(self):
		if not self.isConnected():
			self.device = xled.discover.discover(timeout=5)
			if self.device is not None:
				print(f'Discovered Twinkly device {self.device.id}')
				self.control = xled.ControlInterface(self.device.ip_address, self.device.hw_address)
				print('Connected to device')
				self.high = xled.control.HighControlInterface(self.device.ip_address, self.device.hw_address)
				print('Connected as High Control device')
			else:
				print('No Twinkly device found.')

	def isConnected(self):
		return self.control is not None

	def setColor(self, hexcolor):
		"""
		Sets the LED lights to a static color.
		Note that this clears any movie or playlist currently configured.
		"""
		if self.isConnected():
			(r, g, b) = hexToRGB(hexcolor)
			print(f'Setting color to {r}, {g}, {b}...')
			self.high.set_static_color(r, g, b)

	def error(self):
		"""
		Blinks red, then returns to the current color.
		"""
		self.blink(Lights.ERROR_COLOR, self.lastColor)

	def loading(self):
		"""
		Sets the static color to white.
		"""
		self.setColor(Lights.LOADING_COLOR)

	def ready(self):
		"""
		Done loading, returns to default color.
		"""
		self.setColor(Lights.DEFAULT_COLOR)

	def blink(self, blinkColor, nextColor = DEFAULT_COLOR):
		"""
		Kicks of a background thread to blink the given colors without waiting.
		"""
		if self.isConnected():
			thread = threading.Thread(target=self.blinkAsync, args=(blinkColor, nextColor))
			thread.start()

	def blinkAsync(self, blinkColor, nextColor):
		"""
		Blinks the first color 3 times, then stays on
		the next color.
		"""
		for i in range(3):
			self.setColor(blinkColor)
			time.sleep(0.3)
			self.setColor(Lights.BLINK_OFF_COLOR)
			time.sleep(0.2)
		self.setColor(nextColor)
		self.lastColor = nextColor
