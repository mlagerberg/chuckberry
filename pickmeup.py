import os
import re
import serial
import sys
import time
import _thread

class PickMeUp:

	PICKUP_COMMAND = re.compile(r"XR\[PU([0-9]{3})\]")
	PUTBACK_COMMAND = re.compile(r"XR\[PB([0-9]{3})\]")
	# @TODO This regex only finds the last item in the list (in testRegex, this is d013.
	# This is not a problem while we care about a single tag on the sensor currently, but
	# should be fixed eventually.
	SCAN_RETURN = re.compile(r"X[0-9]{3}B\[(\s*d([0-9]{3}))*\]")

	def testRegex():
		"""
		Testing playground for the regular expressions
		"""
		print('Testing regex...')
		matchPU = PickMeUp.PICKUP_COMMAND.match('XR[PU004]')
		matchPB = PickMeUp.PUTBACK_COMMAND.match('XR[PB004]')
		matchSR = PickMeUp.SCAN_RETURN.match('X001B[ d011 d012 d013]')
		print(matchPU)
		print(matchPB)
		print(matchSR)
		print(matchPU.group())
		print(matchPB.group())
		print(matchSR.group())
		groupPU = PickMeUp.PICKUP_COMMAND.search('XR[PU004]').groups()
		groupPB = PickMeUp.PUTBACK_COMMAND.search('XR[PB004]').groups()
		groupSR = PickMeUp.SCAN_RETURN.findall('X001B[ d011 d012 d013]')
		print(groupPU)
		print(groupPB)
		print(groupSR[0][1])

	def __init__(self, pickUpCallback, putBackCallback, silent = False):
		self.silent = silent
		self.connection = None
		self.lastTag = -1
		self.lastTagTime = -1
		self.pickUpCallback = pickUpCallback
		self.putBackCallback = putBackCallback

	def isConnected(self):
		return self.connection is not None

	def connect(self):
		if not self.isConnected():
			# Serial takes these two parameters: serial device and baudrate.
			# Discover name by running
			# dmesg | grep tty
			try:
				self.connection = serial.Serial('/dev/ttyUSB0', 115200)
			except SerialException:
				print( ("Unable to connect to sensor. Please check if device is running, and "
					   	"if /dev/ttyUSB0 is the correct address by running `dmesg | grep tty` "
						"Update pickmeup.py if needed.") )

	def scan(self):
		"""
		Sends the scan command to the sensor plugged into port 2 on the controller.
		This *should* result in a PickMeUp.SCAN_RETURN command, but in my experience, doesn't.
		"""
		if self.isConnected():
			if not self.silent:
				print('Scanning for present tags...')
			self.writeSensor('X002B[]')

	def setLEDBehaviour(self, behaviour):
		"""
		1 = LED on
		2 = LED off
		3 = LED on, off when tag is present (default)
		4 = LED off, on when tag is present
		"""
		if self.isConnected:
			behaviour = int(behaviour)
			if not behaviour > 0 and not behaviour <= 4:
				print(f'LED behaviour should be a value between 1 and 4')
				return
			if not self.silent:
				print(f'Setting LED behaviour to {behaviour}')
			self.writeSensor(f'X002S[1:{behaviour}]')

	def setGainLevel(self, gain):
		"""
		1. 23 dB, minimum detection range
		2. 33 dB, medium detection range
		3. 38 dB, high detection range (default)
		4. 43 dB, very high detection range
		5. 48 dB, very high detection range
		"""
		if self.isConnected:
			gain = int(gain)
			if not gain > 0 and not gain <= 5:
				print(f'Gain should be a value between 1 and 5')
				return
			if not self.silent:
				print(f'Setting antenna gain to {gain}')
			self.writeSensor(f'X002S[4:{gain}]')

	def setGhostFilter(self, level):
		"""
		Level should be between 1-20 (default: 2)
		Prevents ghost pickups.
		"""
		if self.isConnected:
			level = int(level)
			if not level > 0 and level <= 20:
				print(f'Filter level for ghost pick-ups should be between 1 and 20')
				return
			if not self.silent:
				print(f'Setting filter for ghost pick-ups to {level}')
			self.writeSensor(f'X002S[6:{level}]')

	def writeSensor(self, message):
		"""
		Sends a message to the sensor.
		"""
		if self.isConnected:
			if not self.silent:
				print(f'>>> {message}')
			self.connection.write(message.encode())

	def readSensor(self):
		"""
		Waits for input from the sensor, and calls
		self.processLine when anything arrives.
		"""
		if self.isConnected():
			if not self.silent:
				print('Waiting for sensor input...')
			while True:
				line = self.connection.readline().decode()
				if len(line) > 0:
					if not self.silent:
						print(f'<<< {line}')
					self.processLine(line)
				time.sleep(0.1)

	def processLine(self, line):
		"""
		Put back tag 4: XR[PB004]
		On antenna 0: 	X001A[0]
		Pick up tag 4: 	XR[PU004]
		From antenna 0: X001A[1]
		"""
		if len(line) == 0:
			print('Command too short')
		elif line.startswith('XR'):
			self.parseTagCommand(line)
		elif 'd' in line:
			self.parseScanReturn(line)
		elif line.startswith('X0'):
			self.parseAntennaCommand(line)
		else:
			print('Unknown command')

	def parseTagCommand(self, command):
		matchPU = PickMeUp.PICKUP_COMMAND.match(command)
		matchPB = PickMeUp.PUTBACK_COMMAND.match(command)
		if matchPU is not None:
			tagNumberStr = PickMeUp.PICKUP_COMMAND.search(command).groups()[0]
			self.pickupTag(int(tagNumberStr))
		elif PickMeUp.PUTBACK_COMMAND.match(command) is not None:
			tagNumberStr = PickMeUp.PUTBACK_COMMAND.search(command).groups()[0]
			self.putbackTag(int(tagNumberStr))
		else:
			print('Unknown tag command')

	def parseScanReturn(self, result):
		matchSR = PickMeUp.SCAN_RETURN.match(result)
		if matchSR is not None:
			tagNumbers = PickMeUp.SCAN_RETURN.search(result).groups()[0]
			self.putbackTag(int(tabNumbers[1]))
		else:
			print('Unknown tag command')

	def parseAntennaCommand(self, command):
		# @TODO implement if needed
		pass

	def pickupTag(self, tag):
		if not self.silent:
			print(f'Tag {tag} was picked up')
		self.pickUpCallback(tag)

	def putbackTag(self, tag):
		if not self.silent:
			print(f'Tag {tag} was put back')
		self.putBackCallback(tag)

	def startThread(self):
		try:
			_thread.start_new_thread( self.readSensor, () )
			return True
		except:
			print('Unable to start thread')
			return False
