from playsound import playsound
from picotts import PicoTTS
import pygame
import pyttsx3
import wave
from tempfile import NamedTemporaryFile
from gtts import gTTS
from io import BytesIO
from io import StringIO

class TTS:

	ESPEAK = 0
	GTTS = 1
	PICO = 2

	def __init__(self, speaker = 0):
		self.speaker = speaker
		if self.speaker == TTS.ESPEAK:
			self.espeak = pyttsx3.init()
			# This voice only works on Linux espeak, not Windows or Mac:
			self.espeak.setProperty('voice', 'english_rp+f3')
			self.espeak.setProperty('rate', 160)
		elif self.speaker == TTS.GTTS:
			pygame.mixer.init()
		elif self.speaker == TTS.PICO:
			self.pico = PicoTTS()

	def say(self, msg):
		print(msg)
		if self.speaker == TTS.ESPEAK:
			self.espeak.say(msg)
			self.espeak.runAndWait()
		elif self.speaker == TTS.GTTS:
			#fp = BytesIO()
			tts = gTTS(text=msg, lang='en')
			#tts.write_to_fp(fp)
			#fp.seek(0)
			tts.write_to_fp(fp := NamedTemporaryFile())
			#pygame.mixer.music.load(fp.name)
			#pygame.mixer.music.play()
			playsound(fp.name)
			fp.close()
		elif self.speaker == TTS.PICO:
			wavs = self.pico.synth_wav(msg)
			wav = wave.open(StringIO.StringIO(wavs))
			pass
