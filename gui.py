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
	def __init__(self, blank_icon_path=None):
		super(Card, self).__init__()

		self.pos_state   = None  # False: down; True: up
		self.match_state = False # False: non-matched yet

		# define QPushButton properties
		self.setFixedSize(config.BUTTON_SIZE,config.BUTTON_SIZE)
		self.setDefault(True)
		self.setAutoDefault(False)

	# https://stackoverflow.com/questions/20722823/qt-get-mouse-pressed-event-even-if-a-button-is-pressed
	def mousePressEvent(self, ev):
		QtWidgets.QMessageBox.warning(self, u'Mouse device', config.MOUSE_ERROR_MSG)

	def set_icon(self, icon_path):
		self.icon = QtGui.QIcon(QtGui.QPixmap(icon_path))
		self.setIcon(self.icon)
		self.setIconSize(QtCore.QSize(config.ICON_SIZE,config.ICON_SIZE))

class Board(QtWidgets.QMainWindow):
	def __init__(self):
		super(Board, self).__init__()
		self.match_counter = 0
		self.click_tracker = deque(maxlen=2)
		self.move_tracker  = deque(maxlen=2)

		self.center_coord  = ( (config.BOARD_DIM+1)//2, (config.BOARD_DIM+1)//2 )
		self.corner_pair   = None
		self.top_path      = []
		self.top_direct    = []
		self.bottom_path   = []
		self.bottom_direct = []

		self.stream = None
		self.grid   = None

		self.draw_board()

	def draw_board(self):
		blank_icon_path = os.path.join(config.LINES_ICON_DIR, 'blank.png')
		self.grid = QtWidgets.QGridLayout()
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				card = Card()
				card.set_icon(blank_icon_path)
				self.grid.addWidget(card, i, j)

		# draw arrow borders
		for i in range(config.BOARD_DIM+2):
			if i == (config.BOARD_DIM+1) // 2:
				dir_pos = { 'up'  :(0, i), 'down' :(config.BOARD_DIM+1, i),
							'left':(i, 0), 'right':(i, config.BOARD_DIM+1) }
				for d in dir_pos:
					arrow_icon_path = os.path.join(
								config.ARROW_ICON_DIR, 'arrow_'+d+'_black.png')
					card = Card()
					card.set_icon(arrow_icon_path)
					self.grid.addWidget(card, dir_pos[d][0], dir_pos[d][1])
			else:
				card = Card()
				card.setVisible(False)
				self.grid.addWidget(card, 0, i)
				self.grid.addWidget(card, i, 0)
				self.grid.addWidget(card, i, config.BOARD_DIM+1)
				self.grid.addWidget(card, config.BOARD_DIM+1, i)

		# set main ui
		wg_central = QtWidgets.QWidget()
		wg_central.setLayout(self.grid)
		self.setCentralWidget(wg_central)

		# set cursor to the central element 
		self.grid.itemAtPosition(self.center_coord[0],self.center_coord[1]).widget().setFocus()
		self.grid.itemAtPosition(self.center_coord[0],self.center_coord[1]).widget().setStyleSheet(config.HOVER_FOCUS)

		# create shortcuts for keyboard arrows
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up),    self, self.on_up)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down),  self, self.on_down)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left),  self, self.on_left)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self, self.on_right)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'),            self, self.close)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+I'),            self, self.about)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+T'),            self, self.draw_top_path)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+B'),            self, self.draw_bottom_path)

	def calc_random_paths(self): # FIXME
		blank_icon_path = os.path.join(config.LINES_ICON_DIR, 'blank.png')
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				if (i,j) != self.center_coord:
					button = self.grid.itemAtPosition(i, j)
					button.widget().set_icon(blank_icon_path)

		if np.random.choice((0,1)):
			# pair: top left , bottom right
			self.corner_pair = ( (1,1), (config.BOARD_DIM,config.BOARD_DIM) )
			directions = (('u','l'), ('r','d'))
		else:
			# pair: top right, bottom left
			self.corner_pair = ( (1,config.BOARD_DIM), (config.BOARD_DIM,1) ) 
			directions = (('u','r'), ('l','d'))

		# define top path
		curr_coord = self.center_coord
		self.top_path   = []
		self.top_direct = []
		while curr_coord != self.corner_pair[0]:
			next_direct = np.random.choice(directions[0])
			if next_direct == 'u':
				x = curr_coord[0]-1
				y = curr_coord[1]
				if x < 1:
					continue
			elif next_direct == 'l':
				x = curr_coord[0]
				y = curr_coord[1]-1
				if y < 1:
					continue
			elif next_direct == 'r':
				x = curr_coord[0]
				y = curr_coord[1]+1
				if y > config.BOARD_DIM:
					continue
			next_coord = (x,y)
			if next_coord != self.corner_pair[0]:
				self.top_path.append(tuple(next_coord))
			self.top_direct.append(next_direct)
			curr_coord = next_coord

		# define bottom path
		curr_coord = self.center_coord
		self.bottom_path   = []
		self.bottom_direct = []
		while curr_coord != self.corner_pair[1]:
			next_direct = np.random.choice(directions[1])
			if next_direct == 'd':
				x = curr_coord[0]+1
				y = curr_coord[1]
				if x > config.BOARD_DIM:
					continue
			elif next_direct == 'l':
				x = curr_coord[0]
				y = curr_coord[1]-1
				if y < 1:
					continue
			elif next_direct == 'r':
				x = curr_coord[0]
				y = curr_coord[1]+1
				if y > config.BOARD_DIM:
					continue
			next_coord = (x,y)
			if next_coord != self.corner_pair[1]: # FIXME
				self.bottom_path.append(tuple(next_coord))
			self.bottom_direct.append(next_direct)
			curr_coord = next_coord

	def flash_arrow(self, color, coord):
		if color == 'red':
			pass
		elif color == 'yellow':
			pass
		elif color == 'green':
			pass

	def draw_top_path(self):
		self.calc_random_paths()
		button = self.grid.itemAtPosition(self.corner_pair[0][0], self.corner_pair[0][1])
		button.widget().set_icon(os.path.join(config.LINES_ICON_DIR, 'mountain_top.png'))
		for i in range(len(self.top_path)):
			button = self.grid.itemAtPosition(self.top_path[i][0], self.top_path[i][1])
			icon_file = ''.join(d for d in self.top_direct[i:i+2]) + '.png'
			button.widget().set_icon(os.path.join(config.LINES_ICON_DIR, icon_file))
		if self.corner_pair[0].count(1) == 2:
			icon_file = os.path.join(config.LINES_ICON_DIR, 'climb_up_left') + '.png'
		else: 
			icon_file = os.path.join(config.LINES_ICON_DIR, 'climb_up_right') + '.png'
		button = self.grid.itemAtPosition(self.center_coord[0], self.center_coord[1])
		button.widget().set_icon(icon_file)
		# set cursor to the central element 
		self.grid.itemAtPosition(self.center_coord[0],self.center_coord[1]).widget().setFocus()
		self.grid.itemAtPosition(self.center_coord[0],self.center_coord[1]).widget().setStyleSheet(config.HOVER_FOCUS)

	def draw_bottom_path(self):
		self.calc_random_paths()
		button = self.grid.itemAtPosition(self.corner_pair[1][0], self.corner_pair[1][1])
		button.widget().set_icon(os.path.join(config.LINES_ICON_DIR, 'house_camp.png'))
		for i in range(len(self.bottom_path)):
			button = self.grid.itemAtPosition(self.bottom_path[i][0], self.bottom_path[i][1])
			icon_file = ''.join(d for d in self.bottom_direct[i:i+2]) + '.png'
			button.widget().set_icon(os.path.join(config.LINES_ICON_DIR, icon_file))
		if self.corner_pair[1].count(5) == 2: 
			icon_file = os.path.join(config.LINES_ICON_DIR, 'climb_down_right') + '.png'
		else: 
			icon_file = os.path.join(config.LINES_ICON_DIR, 'climb_down_left') + '.png'
		button = self.grid.itemAtPosition(self.center_coord[0], self.center_coord[1])
		button.widget().set_icon(icon_file)
		# set cursor to the central element 
		self.grid.itemAtPosition(self.center_coord[0],self.center_coord[1]).widget().setFocus()
		self.grid.itemAtPosition(self.center_coord[0],self.center_coord[1]).widget().setStyleSheet(config.HOVER_FOCUS)

	def about(self):
		QtWidgets.QMessageBox.information(self, u'About', config.INFO)
		return

	#self.wav = sound.MATCH
	#threading.Thread(target=self.play, args=(1.5,)).start()
	#self.wav = sound.UNMATCH
	#threading.Thread(target=self.play, args=(1.0,)).start()

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

		if new_row   > config.BOARD_DIM:
			new_row  = config.BOARD_DIM  # limit the fucking right edge
			play_sound = False
		elif new_row < 1:
			new_row  = 1                   # limit the fucking left edge
			play_sound = False

		if new_col   > config.BOARD_DIM:
			new_col  = config.BOARD_DIM  # limit the fucking bottom edge
			play_sound = False
		elif new_col < 1:
			new_col  = 1                   # limit the fucking top edge
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
