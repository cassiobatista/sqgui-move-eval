#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

import os
import wave
import pyaudio

import config

MOVE     = wave.open(os.path.join(config.SOUNDS_DIR, 'press_02.wav'),    'rb')
OUTBOUND = wave.open(os.path.join(config.SOUNDS_DIR, 'outbound_01.wav'), 'rb')
MATCH    = wave.open(os.path.join(config.SOUNDS_DIR, 'match_01.wav'),    'rb')
UNMATCH  = wave.open(os.path.join(config.SOUNDS_DIR, 'unmatch_01.wav'),  'rb')
WIN      = wave.open(os.path.join(config.SOUNDS_DIR, 'win_01.wav'),      'rb')
REG_BEEP = wave.open(os.path.join(config.SOUNDS_DIR, 'regular_countdown_beep.wav'), 'rb')
END_BEEP = wave.open(os.path.join(config.SOUNDS_DIR, 'final_countdown_beep.wav'),   'rb')

p = pyaudio.PyAudio()
### EOF ###
