#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

import sys
import os
import time
import pyaudio
import numpy as np

import threading 
from collections import deque
from PyQt5 import QtWidgets, QtGui, QtCore
from termcolor import colored

import config
import sound

class Card(QtWidgets.QPushButton):
	def __init__(self, icon_index, face_icon_path, back_icon_path):
		super(Card, self).__init__()
		self.face_icon = QtGui.QIcon(QtGui.QPixmap(face_icon_path))
		self.back_icon = QtGui.QIcon(QtGui.QPixmap(back_icon_path))

		self.icon_index  = icon_index
		self.pos_state   = None  # False: down; True: up
		self.match_state = False # False: non-matched yet

		# define QPushButton properties
		self.setMinimumSize(100,100)
		self.setMaximumSize(150,150)
		self.setDefault(True);
		self.setAutoDefault(False);
		self.clicked.connect(self.toggle_card)

		# make sure card starts face down
		self.toggle_card()

	# https://stackoverflow.com/questions/20722823/qt-get-mouse-pressed-event-even-if-a-button-is-pressed
	def mousePressEvent(self, ev):
		QtWidgets.QMessageBox.warning(self, u'Mouse device', config.MOUSE_ERROR_MSG)

	def toggle_card(self):
			icon = self.face_icon
			self.setIcon(icon)
			self.setIconSize(QtCore.QSize(75,75))

class Board(QtWidgets.QMainWindow):
	def __init__(self):
		super(Board, self).__init__()
		self.match_counter = 0
		self.click_tracker = deque(maxlen=2)
		self.move_tracker  = deque(maxlen=2)

		self.stream = None

		self.load_card_icons()
		self.draw_board()

	def load_card_icons(self):
		icon_folder = os.path.join(config.ICONS_DIR)
		filenames = np.random.choice(os.listdir(os.path.join(icon_folder)),
					config.NUM_CARDS, replace=False)
		self.card_icon_paths = []
		for f in filenames:
			self.card_icon_paths.append(os.path.join(icon_folder, f))

	def draw_board(self):
		question_icon_path = os.path.join(config.RESOURCES_DIR, 'question.png')
		self.grid = QtWidgets.QGridLayout()
		for i in range(config.BOARD_ROWS):
			for j in range(config.BOARD_COLS):
				face_icon_path = self.card_icon_paths[self.card_pairs[i][j]]
				card = Card(self.card_pairs[i][j], face_icon_path, question_icon_path)
				card.clicked.connect(self.check_match)
				self.grid.addWidget(card, i, j)

		# set main ui
		wg_central = QtWidgets.QWidget()
		wg_central.setLayout(self.grid)
		self.setCentralWidget(wg_central)

		# set cursor to the first element at the top-left corner
		self.grid.itemAtPosition(0,0).widget().setFocus()
		self.grid.itemAtPosition(0,0).widget().setStyleSheet(config.HOVER_FOCUS)
		self.move_tracker.append((0, 0, self.card_pairs[0][0]))

		# create shortcuts for keyboard arrows
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up),    self, self.on_up)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down),  self, self.on_down)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left),  self, self.on_left)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self, self.on_right)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'),            self, self.close)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+I'),            self, self.about)

	def about(self):
		QtWidgets.QMessageBox.information(self, u'About', config.INFO)
		return

	def check_match(self):
		if config.DEGUB:
			print('pres1', colored(list(self.move_tracker), 'red'), 
						colored(list(self.click_tracker), 'green'))
		if len(self.click_tracker) == self.click_tracker.maxlen:
			self.restore_after_unmatch(from_click=True)
			self.wav = sound.MOVE
			threading.Thread(target=self.play, args=(2.0)).start()
			return

		self.click_tracker.append(self.move_tracker[-1])
		if len(self.click_tracker) == self.click_tracker.maxlen:
			matches = [midx[2] for midx in self.click_tracker]
			if len(set(matches)) == 1:
				rows = [mx[0] for mx in self.click_tracker]
				cols = [my[1] for my in self.click_tracker]
				if (rows[0],cols[0]) == (rows[1],cols[1]):
					self.click_tracker.clear()
					threading.Thread(target=self.play, 
								args=(sound.UNMATCH, 1.0,)).start()
					return
				for i in range(2):
					button = self.grid.itemAtPosition(rows[i], cols[i])
					button.widget().set_matched(True)
				self.match_counter += 1
				if self.match_counter == config.NUM_CARDS:
					self.win()
				else:
					self.wav = sound.MATCH
					threading.Thread(target=self.play, args=(1.5,)).start()
			else:
				self.wav = sound.UNMATCH
				threading.Thread(target=self.play, args=(1.0,)).start()
		if config.DEGUB:
			print('pres2', colored(list(self.move_tracker), 'red'), 
						colored(list(self.click_tracker), 'green'))

	def close(self):
		if self.stream is not None and self.stream.is_active():
			self.stream.stop_stream()
		sound.MOVE.close()
		sound.OUTBOUND.close()
		sound.MATCH.close()
		sound.UNMATCH.close()
		sound.WIN.close()
		sound.p.terminate()
		QtWidgets.qApp.quit()

	def win(self):
		self.wav = sound.WIN
		threading.Thread(target=self.play, args=(1.0,)).start()
		reply = QtWidgets.QMessageBox.information(self, 
					u'You win', config.WIN_MSG, QtWidgets.QMessageBox.Ok)
		self.close()

	def on_up(self):
		if config.DEGUB:
			print('   up', end=' ')
		self.move_focus(0, -1)

	def on_down(self):
		if config.DEGUB:
			print(' down', end=' ')
		self.move_focus(0, +1)

	def on_left(self):
		if config.DEGUB:
			print(' left', end=' ')
		self.move_focus(-1, 0)

	def on_right(self):
		if config.DEGUB:
			print('right', end=' ')
		self.move_focus(+1, 0)

	def move_focus(self, dx, dy):
		if QtWidgets.qApp.focusWidget() == 0:
			return

		idx = self.grid.indexOf(QtWidgets.qApp.focusWidget())
		if idx == -1:
			return

		r, c, row_span, col_span = self.grid.getItemPosition(idx)
		new_row = r + dy
		new_col = c + dx

		play_sound = True

		if new_row   > config.BOARD_ROWS-1:
			new_row  = config.BOARD_ROWS-1 # limit the fucking right edge
			play_sound = False
		elif new_row < 0:
			new_row  = 0                   # limit the fucking left edge
			play_sound = False

		if new_col   > config.BOARD_COLS-1:
			new_col  = config.BOARD_COLS-1 # limit the fucking bottom edge
			play_sound = False
		elif new_col < 0:
			new_col  = 0                   # limit the fucking top edge
			play_sound = False

		if self.stream is not None and self.stream.is_active():
			self.stream.stop_stream()
			sound.MOVE.rewind()
			sound.OUTBOUND.rewind()

		if play_sound:
			self.wav = sound.MOVE
		else:
			self.wav = sound.OUTBOUND
		threading.Thread(target=self.play, args=(2.0,)).start()

		button = self.grid.itemAtPosition(new_row, new_col)
		if button is None:
			return

		button.widget().setFocus()
		button.widget().setStyleSheet(config.HOVER_FOCUS)
		self.move_tracker.append(
					(new_row, new_col, self.card_pairs[new_row][new_col]))
		if config.DEGUB:
			print(colored(list(self.move_tracker), 'red'), 
						colored(list(self.click_tracker), 'green'))

	def play(self, freq_factor):
		self.wav.rewind()
		if self.stream is not None and self.stream.is_active():
			self.stream.stop_stream()
		self.stream = sound.p.open(
					format=sound.p.get_format_from_width(self.wav.getsampwidth()),
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

if __name__=='__main__':
	app = QtWidgets.QApplication(sys.argv)
	window = Board()
	window.move(300,50)
	window.setWindowTitle(config.WINDOW_TITLE)
	window.show()
	sys.exit(app.exec_())
### EOF ###
