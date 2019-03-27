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
	MATCH      = 0
	UNMATCH    = 1
	WIN        = 2
	REG_BEEP   = 3
	FINAL_BEEP = 4
	def __init__(self):
		super(Sound, self).__init__()
		self.stream  = None
		self.wav     = None
		self.effects = []
		self.p       = pyaudio.PyAudio()
		self.open()

	def play(self, eff_idx, freq):
		if config.SOUND_USED:
			threading.Thread(target=self.play_bg, args=(eff_idx, freq,)).start()

	def play_bg(self, eff_index, freq_factor):
		self.wav = self.effects[eff_index]
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
		self.effects.append(wave.open(os.path.join(config.SOUNDS_DIR, 'match_01.wav'),     'rb'))
		self.effects.append(wave.open(os.path.join(config.SOUNDS_DIR, 'unmatch_01.wav'),   'rb'))
		self.effects.append(wave.open(os.path.join(config.SOUNDS_DIR, 'win_01.wav'),       'rb'))
		self.effects.append(wave.open(os.path.join(config.SOUNDS_DIR, 'reg_cd_beep.wav'),  'rb'))
		self.effects.append(wave.open(os.path.join(config.SOUNDS_DIR, 'final_cd_beep.wav'),'rb'))

	def close(self):
		if self.stream is not None:
			self.stream.stop_stream()
			self.stream.close()
			self.stream = None
		for eff in self.effects:
			eff.close()
		self.p.terminate()
### EOF ###
