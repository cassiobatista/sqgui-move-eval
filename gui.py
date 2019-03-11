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

class Blink(QtCore.QThread):
	signal = QtCore.pyqtSignal('PyQt_PyObject')
	def __init__(self):
		super(Blink, self).__init__()

class Arrow(QtWidgets.QPushButton):
	def __init__(self):
		super(Arrow, self).__init__()

class Card(QtWidgets.QPushButton):
	def __init__(self, blank_icon_path=None):
		super(Card, self).__init__()

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
		self.is_path_set = False
		self.coord = {
			'center'     :((config.BOARD_DIM+1)//2, (config.BOARD_DIM+1)//2),
			'arrow_up'   :(0,                       (config.BOARD_DIM+1)//2),
			'arrow_down' :(config.BOARD_DIM+1,      (config.BOARD_DIM+1)//2),
			'arrow_left' :((config.BOARD_DIM+1)//2, 0),
			'arrow_right':((config.BOARD_DIM+1)//2, (config.BOARD_DIM+1)),
			'corner_target':(),
			'corner_top_left'    :(1,                1),
			'corner_top_right'   :(1,                config.BOARD_DIM),
			'corner_bottom_left' :(config.BOARD_DIM, 1),
			'corner_bottom_right':(config.BOARD_DIM, config.BOARD_DIM),
		}

		self.currs = {
			'part' :0,    # 0:up, 1:down
			'move' :None,
			'coord':self.coord['center'],
			'index':None,
		}

		self.counters = {
			'moves' :0,
			'errors':0,
		}

		self.climbing = {
			'up_path'  :[],
			'down_path':[],
			'up_directions'  :[],
			'down_directions':[]
		}

		self.corner_pair     = ()

		self.stream = None
		self.grid   = None

		self.draw_board()
		self.draw_borders()
		self.set_ui_elements()

	def place_cursor_at_center(self, focus):
		self.grid.itemAtPosition(self.coord['center'][0],
					self.coord['center'][1]).widget().setFocus()
		self.grid.itemAtPosition(self.coord['center'][0],
					self.coord['center'][1]).widget().setStyleSheet(focus)

	def draw_borders(self):
		for i in range(config.BOARD_DIM+2):
			if i == (config.BOARD_DIM+1) // 2:
				for karrow in self.coord:
					if 'arrow' in karrow:
						arrow_icon_path = os.path.join(
									config.ARROW_ICON_DIR, karrow + '_trans.png')
						card = Card()
						card.set_icon(arrow_icon_path)
						self.grid.addWidget(card,
									self.coord[karrow][0], self.coord[karrow][1])
			else:
				card = Card()
				card.setVisible(False)
				self.grid.addWidget(card, 0, i)
				self.grid.addWidget(card, i, 0)
				self.grid.addWidget(card, i, config.BOARD_DIM+1)
				self.grid.addWidget(card, config.BOARD_DIM+1, i)

	def draw_board(self):
		blank_icon_path = os.path.join(config.LINES_ICON_DIR, 'blank.png')
		self.grid = QtWidgets.QGridLayout()
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				card = Card()
				card.set_icon(blank_icon_path)
				card.setEnabled(False)
				self.grid.addWidget(card, i, j)

	def set_ui_elements(self):
		wg_central = QtWidgets.QWidget()
		wg_central.setLayout(self.grid)
		self.setCentralWidget(wg_central)

		# set cursor to the central element 
		self.place_cursor_at_center(config.HOVER_FOCUS_DISABLED)

		# https://www.tutorialspoint.com/pyqt/pyqt_qstatusbar_widget.htm
		self.status_bar = QtWidgets.QStatusBar()
		self.status_bar.showMessage(u'TIP: press CTRL+H for help', 5000)
		self.setStatusBar(self.status_bar)

		# create shortcuts for keyboard arrows
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up),    self, self.on_up)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down),  self, self.on_down)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left),  self, self.on_left)
		QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self, self.on_right)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'),            self, self.close)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+I'),            self, self.about)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+H'),            self, self.help)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+L'),            self, self.calc_random_paths)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+1'),            self, self.draw_top_path)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+2'),            self, self.draw_bottom_path)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+R'),            self, self.reset_board)
		QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+P'),            self, self.start_game) 

	# TODO
	def start_game(self, curr_half='up'):
		if curr_half == 'up':
			self.draw_top_path()

	def reset_board(self):
		blank_icon_path = os.path.join(config.LINES_ICON_DIR, 'blank.png')
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				button = self.grid.itemAtPosition(i, j)
				button.widget().set_icon(blank_icon_path)
				button.widget().setEnabled(False)

		self.counters['moves']  = 0
		self.counters['errors'] = 0
		self.currs['coord'] = self.coord['center']
		self.currs['index'] = 0

		self.climbing = {
			'up_path'  :[],
			'down_path':[],
			'up_directions'  :[],
			'down_directions':[]
		}

		self.corner_pair     = ()
		self.is_path_set = False

	def set_board(self):
		blank_icon_path = os.path.join(config.LINES_ICON_DIR, 'blank.png')
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				if (i,j) != self.coord['center']:
					button = self.grid.itemAtPosition(i, j)
					button.widget().set_icon(blank_icon_path)
					button.widget().setEnabled(True)
		button = self.grid.itemAtPosition(
					self.coord['center'][0], self.coord['center'][1])
		button.widget().setEnabled(True)
		self.is_path_set = True

	def calc_random_paths(self): # FIXME
		self.reset_board()
		self.set_board()
		if np.random.choice((0,1)):
			self.corner_pair      = (self.coord['corner_top_right'], self.coord['corner_bottom_left'])
			self.path_orientation = (('up','right'), ('down','left'))
		else:
			self.corner_pair     = (self.coord['corner_top_left'], self.coord['corner_bottom_right'])
			self.path_orientation = (('up','left'), ('down','right'))

		directions = ('up','down')
		for i in range(2):
			curr_coord = self.coord['center']
			self.climbing[directions[i] + '_path'] = []
			self.climbing[directions[i] + '_directions'] = []
			while curr_coord != self.corner_pair[i]:
				next_direct = np.random.choice(self.path_orientation[i])
				if next_direct == 'up':
					x = curr_coord[0]-1
					y = curr_coord[1]
					if x < 1:
						continue
				elif next_direct == 'down':
					x = curr_coord[0]+1
					y = curr_coord[1]
					if x > config.BOARD_DIM:
						continue
				elif next_direct == 'left':
					x = curr_coord[0]
					y = curr_coord[1]-1
					if y < 1:
						continue
				elif next_direct == 'right':
					x = curr_coord[0]
					y = curr_coord[1]+1
					if y > config.BOARD_DIM:
						continue
				next_coord = (x,y)
				if next_coord != self.corner_pair[i]:
					self.climbing[directions[i] + '_path'].append(next_coord)
				self.climbing[directions[i] + '_directions'].append(next_direct[0])
				curr_coord = next_coord
		self.draw_top_path()

	def draw_top_path(self):
		if not self.is_path_set:
			return
		self.set_board()
		button = self.grid.itemAtPosition(
					self.corner_pair[0][0], self.corner_pair[0][1])
		button.widget().set_icon(os.path.join(
					config.CLIMB_ICON_DIR, 'mountain_top_no_climber.png'))
		for i in range(len(self.climbing['up_path'])):
			button = self.grid.itemAtPosition(
						self.climbing['up_path'][i][0], self.climbing['up_path'][i][1])
			png = ''.join(d for d in self.climbing['up_directions'][i:i+2]) + '.png'
			button.widget().set_icon(os.path.join(config.LINES_ICON_DIR, png))
		if self.corner_pair[0] == self.coord['corner_top_left']:
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_left') + '.png'
		else: 
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_right') + '.png'
		button = self.grid.itemAtPosition(
					self.coord['center'][0], self.coord['center'][1])
		button.widget().set_icon(png)
		self.place_cursor_at_center(config.HOVER_FOCUS_LOADED)

	def draw_bottom_path(self):
		if not self.is_path_set:
			return
		self.set_board()
		button = self.grid.itemAtPosition(self.corner_pair[1][0], self.corner_pair[1][1])
		button.widget().set_icon(os.path.join(
					config.CLIMB_ICON_DIR, 'house_camp_no_climber.png'))
		for i in range(len(self.climbing['down_path'])):
			button = self.grid.itemAtPosition(
						self.climbing['down_path'][i][0], self.climbing['down_path'][i][1])
			png = ''.join(d for d in self.climbing['down_directions'][i:i+2]) + '.png'
			button.widget().set_icon(os.path.join(config.LINES_ICON_DIR, png))
		if self.corner_pair[1] == self.coord['corner_bottom_right']:
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_right') + '.png'
		else: 
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_left') + '.png'
		button = self.grid.itemAtPosition(
					self.coord['center'][0], self.coord['center'][1])
		button.widget().set_icon(png)
		self.place_cursor_at_center(config.HOVER_FOCUS_LOADED)

	def help(self):
		QtWidgets.QMessageBox.information(self, u'Help', config.HELP_MSG)
		return

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
		self.counters['moves'] += 1
		self.currs['move'] = 'up'
		self.move_focus(0, -1)

	def on_down(self):
		self.counters['moves'] += 1
		self.currs['move'] = 'down'
		self.move_focus(0, +1)

	def on_left(self):
		self.counters['moves'] += 1
		self.currs['move'] = 'left'
		self.move_focus(-1, 0)

	def on_right(self):
		self.counters['moves'] += 1
		self.currs['move'] = 'right'
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
			new_row  = config.BOARD_DIM  # limit the right edge
			play_sound = False
		elif new_row < 1:
			new_row  = 1                 # limit the left edge
			play_sound = False

		if new_col   > config.BOARD_DIM:
			new_col  = config.BOARD_DIM  # limit the bottom edge
			play_sound = False
		elif new_col < 1:
			new_col  = 1                 # limit the top edge
			play_sound = False

		if self.stream is not None and self.stream.is_active():
			self.stream.stop_stream()
			sound.MOVE.rewind()
			sound.OUTBOUND.rewind()

		self.currs['coord'] = (new_row, new_col)
		if self.is_path_set:
			if self.currs['coord'] == self.corner_pair[0]:
				self.win()
			if self.currs['coord'] == self.climbing['up_path'][self.currs['index']]:
				self.currs['index'] += 1
				print('acertou mano')
			else:
				self.counters['errors'] += 1
				print('errou mano')

		if play_sound:
			self.wav = sound.MOVE
		else:
			self.wav = sound.OUTBOUND
		threading.Thread(target=self.play, args=(2.0,)).start()

		button = self.grid.itemAtPosition(new_row, new_col)
		if button is None:
			return

		button.widget().setFocus()
		button.widget().setStyleSheet(config.HOVER_FOCUS_DISABLED)

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
