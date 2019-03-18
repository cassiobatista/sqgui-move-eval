#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

import os
import wave
import time
import pyaudio
import threading

import config

class Sound:
	def __init__(self):
		super(Sound, self).__init__()
		self.stream = None
		self.wav    = None
		self.p      = pyaudio.PyAudio()
		self.open()

	def play(self, freq_factor):
		threading.Thread(target=self.play_bg, args=(freq_factor,)).start()

	def play_bg(self, freq_factor):
		self.wav.rewind()
		if self.stream is not None and self.stream.is_active():
			self.stream.stop_stream()
		self.stream = self.p.open(
					format=self.p.get_format_from_width(self.wav.getsampwidth()),
					channels=self.wav.getnchannels(),
					rate=int(self.wav.getframerate()*freq_factor),
					output=True,
					stream_callback=self.callback)
		self.stream.start_stream()
		while self.stream is not None and self.stream.is_active():
			time.sleep(0.05)
	
		if self.stream is not None:
			self.stream.stop_stream()
			self.stream.close()
			self.stream = None
	
	def callback(self, in_data, frame_count, time_info, status):
		data = self.wav.readframes(frame_count)
		return (data, pyaudio.paContinue)

	def open(self):
		self.MOVE     = wave.open(os.path.join(config.SOUNDS_DIR, 'press_02.wav'),     'rb')
		self.OUTBOUND = wave.open(os.path.join(config.SOUNDS_DIR, 'outbound_01.wav'),  'rb')
		self.MATCH    = wave.open(os.path.join(config.SOUNDS_DIR, 'match_01.wav'),     'rb')
		self.UNMATCH  = wave.open(os.path.join(config.SOUNDS_DIR, 'unmatch_01.wav'),   'rb')
		self.WIN      = wave.open(os.path.join(config.SOUNDS_DIR, 'win_01.wav'),       'rb')
		self.REG_BEEP = wave.open(os.path.join(config.SOUNDS_DIR, 'reg_cd_beep.wav'),  'rb')
		self.END_BEEP = wave.open(os.path.join(config.SOUNDS_DIR, 'final_cd_beep.wav'),'rb')

	def close(self):
		if self.stream is not None:
			self.stream.stop_stream()
			self.stream.close()
			self.stream = None
		self.MOVE.close()
		self.OUTBOUND.close()
		self.MATCH.close()
		self.UNMATCH.close()
		self.WIN.close()
		self.REG_BEEP.close()
		self.END_BEEP.close()
		self.p.terminate()
### EOF ###
