#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

import sys
import os
import numpy as np

from collections import deque
from PyQt5 import QtWidgets, QtGui, QtCore, QtTest
from serial import Serial

import config
from sound import Sound
from button import Card, LightArrow, LightState, LightMachine

class Arduino(Serial):
	def __init__(self):
		super(Arduino, self).__init__(config.ARDUINO_PORT, config.ARDUINO_BAUDRATE)
	
	def send(self):
		self.write(str.encode(config.ARDUINO_MSG))

class Board(QtWidgets.QMainWindow):
	def __init__(self):
		super(Board, self).__init__()
		self.coord = {
			'center'             :((config.BOARD_DIM+1)//2, (config.BOARD_DIM+1)//2),
			'arrow_up'           :(0,                       (config.BOARD_DIM+1)//2),
			'arrow_down'         :(config.BOARD_DIM+1,      (config.BOARD_DIM+1)//2),
			'arrow_left'         :((config.BOARD_DIM+1)//2, 0),
			'arrow_right'        :((config.BOARD_DIM+1)//2, (config.BOARD_DIM+1)),
			'corner_top_left'    :(1,                       1),
			'corner_top_right'   :(1,                       config.BOARD_DIM),
			'corner_bottom_left' :(config.BOARD_DIM,        1),
			'corner_bottom_right':(config.BOARD_DIM,        config.BOARD_DIM),
			'previous_move':(),
			'current_move':(),
			'last_correct':(),
		}

		self.reset_vars()

		if config.ARDUINO_USED:
			self.arduino = Arduino()
		self.sound = Sound()
		self.grid  = QtWidgets.QGridLayout()

		self.draw_board()
		self.draw_arrows()
		self.set_ui_elements()

	def place_cursor_at_center(self, focus):
		central_button = self.grid.itemAtPosition(
					self.coord['center'][0], self.coord['center'][1]).widget()
		central_button.setFocus()
		central_button.setStyleSheet(focus)

	def draw_arrows(self):
		for i in range(config.BOARD_DIM+2):
			if i == (config.BOARD_DIM+1) // 2:
				for karrow in self.coord:
					if 'arrow' not in karrow:
						continue
					arrow_icon_path = os.path.join(
								config.ARROW_ICON_DIR, karrow + '.png')
					arrow = LightArrow(self.sound)
					arrow.set_icon(arrow_icon_path)
					self.grid.addWidget(arrow,
								self.coord[karrow][0], self.coord[karrow][1])
					state   = LightState(arrow)
					machine = LightMachine(self, state)
					self.light_machines[karrow.replace('arrow_','')] = machine
			else:
				card = Card()
				card.setVisible(False)
				self.grid.addWidget(card, 0, i)
				self.grid.addWidget(card, i, 0)
				self.grid.addWidget(card, i, config.BOARD_DIM+1)
				self.grid.addWidget(card, config.BOARD_DIM+1, i)

	def draw_board(self):
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				card = Card()
				card.setEnabled(False)
				self.grid.addWidget(card, i, j)

	def set_ui_elements(self):
		wg_central = QtWidgets.QWidget()
		wg_central.setLayout(self.grid)
		self.setCentralWidget(wg_central)

		# set cursor to the central element 
		self.place_cursor_at_center(config.HOVER_FOCUS_IDLE)

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

	def handle_kb_move(self, icon_path):
		self.sound.play(self.sound.FINAL_BEEP, 1.5)
		QtTest.QTest.qWait(500)
		button = self.grid.itemAtPosition(
					self.coord['center'][0], self.coord['center'][1]).widget()
		button.setFocus()
		button.set_icon(icon_path)
		button.setStyleSheet(config.HOVER_FOCUS_ENABLED)
		if config.ARDUINO_USED:
			self.arduino.send()
		QtTest.QTest.qWait(2500)

	def start_game(self):
		if not self.is_path_set:
			print('error: theres somthign really really wrong around here')
			return

		if self.currs['vdir'] == 'down':
			self.draw_bottom_path()
		elif self.currs['vdir'] == 'up':
			self.draw_top_path()

		while self.currs['index'] < len(self.climbing[self.currs['vdir'] + '_directions']):
			vdir = self.climbing[self.currs['vdir'] + '_directions'][self.currs['index']]
			if vdir == 'u':
				machine = self.light_machines['up']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_up.png')
			elif vdir == 'l':
				machine = self.light_machines['left']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_left.png')
			elif vdir == 'r':
				machine = self.light_machines['right']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_right.png')
			elif vdir == 'd':
				machine = self.light_machines['down']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_down.png')
			machine.start(self.grid)
			QtTest.QTest.qWait(3100)
			machine.stop(self.grid)
			self.handle_kb_move(arrow_icon_path)
		machine.state.light.set_bg_colour('white')

	def reset_vars(self):
		self.is_path_set = False
		self.corner_pair = ()
		self.coord['current_move'] = self.coord['center']
		self.coord['last_correct'] = self.coord['center']
		self.light_machines = { 'up':None, 'down':None, 'left':None, 'right':None }
		self.currs = {
			'vdir' :'up',
			'index':0,
			'num_moves' :0,
			'num_errors':0 }
		self.climbing = {
			'up_path'  :[],
			'down_path':[],
			'up_directions'  :[],
			'down_directions':[] }

	def reset_board(self):
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				button = self.grid.itemAtPosition(i, j).widget()
				button.unset_icon()
				button.setEnabled(False)

	def set_board(self):
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				if (i,j) != self.coord['center']:
					button = self.grid.itemAtPosition(i, j).widget()
					button.unset_icon()
					button.setEnabled(True)
		self.is_path_set = True
		self.grid.itemAtPosition(self.coord['center'][0], 
					self.coord['center'][1]).widget().setEnabled(True)

	def calc_random_paths(self):
		self.reset_board()
		self.set_board()
		if np.random.choice((0,1)):
			self.corner_pair      = (self.coord['corner_top_right'], self.coord['corner_bottom_left'])
			self.path_orientation = (('up','right'), ('down','left'))
		else:
			self.corner_pair      = (self.coord['corner_top_left'], self.coord['corner_bottom_right'])
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
				self.climbing[directions[i] + '_path'].append(next_coord)
				self.climbing[directions[i] + '_directions'].append(next_direct[0])
				curr_coord = next_coord
		self.draw_top_path()

	def draw_top_path(self):
		if not self.is_path_set:
			return
		self.set_board()
		button = self.grid.itemAtPosition(self.corner_pair[0][0], 
					self.corner_pair[0][1]).widget()
		button.set_icon(os.path.join(config.CLIMB_ICON_DIR, 'mountain_top_no_climber.png'))
		for i in range(len(self.climbing['up_path'])-1):
			button = self.grid.itemAtPosition(self.climbing['up_path'][i][0], 
						self.climbing['up_path'][i][1]).widget()
			png = ''.join(d for d in self.climbing['up_directions'][i:i+2]) + '.png'
			button.set_icon(os.path.join(config.LINES_ICON_DIR, png))
		if self.corner_pair[0] == self.coord['corner_top_left']:
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_left') + '.png'
		else: 
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_right') + '.png'
		button = self.grid.itemAtPosition(
					self.coord['center'][0], self.coord['center'][1]).widget()
		button.set_icon(png)
		self.place_cursor_at_center(config.HOVER_FOCUS_IDLE)

	def draw_bottom_path(self):
		if not self.is_path_set:
			return
		self.set_board()
		button = self.grid.itemAtPosition(self.corner_pair[1][0], 
					self.corner_pair[1][1]).widget()
		button.set_icon(os.path.join(config.CLIMB_ICON_DIR, 'house_camp_no_climber.png'))
		for i in range(len(self.climbing['down_path'])-1):
			button = self.grid.itemAtPosition(self.climbing['down_path'][i][0], 
						self.climbing['down_path'][i][1]).widget()
			png = ''.join(d for d in self.climbing['down_directions'][i:i+2]) + '.png'
			button.set_icon(os.path.join(config.LINES_ICON_DIR, png))
		if self.corner_pair[1] == self.coord['corner_bottom_right']:
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_right') + '.png'
		else: 
			png = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_left') + '.png'
		button = self.grid.itemAtPosition(self.coord['center'][0], 
					self.coord['center'][1]).widget()
		button.set_icon(png)
		self.place_cursor_at_center(config.HOVER_FOCUS_IDLE)

	def help(self):
		QtWidgets.QMessageBox.information(self, u'Help', config.HELP_MSG)
		return

	def about(self):
		QtWidgets.QMessageBox.information(self, u'About', config.INFO)
		return

	def close(self):
		for machine in self.light_machines.values():
			if machine.isRunning():
				machine.state.killTimer()
				machine.stop()
		if self.sound.stream is not None and self.sound.stream.is_active():
			self.sound.stream.stop_stream()
		self.sound.close()
		if config.ARDUINO_USED:
			self.arduino.close()
		QtWidgets.qApp.quit()

	def win(self):
		if self.sound.stream is not None and self.sound.stream.is_active():
			self.sound.stream.stop_stream()
		if self.currs['vdir'] == 'up':
			icon = os.path.join(config.CLIMB_ICON_DIR, 'mountain_top_climber.png')
		else:
			icon = os.path.join(config.CLIMB_ICON_DIR, 'house_camp_climber.png')

		button = self.grid.itemAtPosition(self.coord['current_move'][0], 
					self.coord['current_move'][1]).widget()
		button.setFocus()
		button.setStyleSheet(config.HOVER_FOCUS_ENABLED)
		button.set_icon(icon)
		self.sound.play(self.sound.WIN, 1.0)
		reply = QtWidgets.QMessageBox.information(self, u'You did it', 
					config.WIN_MSG % self.currs['vdir'], QtWidgets.QMessageBox.Ok)

		if self.currs['vdir'] == 'down':
			self.sound.close()
			self.close()
		else:
			self.currs['vdir']       = 'down'
			self.currs['index']      = 0
			self.currs['num_moves']  = 0
			self.currs['num_errors'] = 0 
			self.coord['current_move'] = self.coord['center']
			self.coord['last_correct'] = self.coord['center']
			self.start_game()

	def on_up(self):
		self.currs['num_moves'] += 1
		self.move_focus(0, -1)

	def on_down(self):
		self.currs['num_moves'] += 1
		self.move_focus(0, +1)

	def on_left(self):
		self.currs['num_moves'] += 1
		self.move_focus(-1, 0)

	def on_right(self):
		self.currs['num_moves'] += 1
		self.move_focus(+1, 0)

	def move_focus(self, dx, dy):
		if QtWidgets.qApp.focusWidget() == 0:
			return

		idx = self.grid.indexOf(QtWidgets.qApp.focusWidget())
		if idx == -1:
			return

		# remove icon from central button 
		self.grid.itemAtPosition(self.coord['center'][0], 
					self.coord['center'][1]).widget().unset_icon()

		new_row = self.coord['last_correct'][0] + dy
		new_col = self.coord['last_correct'][1] + dx
		if new_row   > config.BOARD_DIM:
			new_row  = config.BOARD_DIM  # limit the right edge
		elif new_row < 1:
			new_row  = 1                 # limit the left edge
		if new_col   > config.BOARD_DIM:
			new_col  = config.BOARD_DIM  # limit the bottom edge
		elif new_col < 1:
			new_col  = 1                 # limit the top edge

		if self.sound.stream is not None and self.sound.stream.is_active():
			self.sound.stream.stop_stream()

		self.coord['previous_move'] = self.coord['current_move']
		self.coord['current_move'] = (new_row, new_col)
		if self.is_path_set:
			if self.coord['current_move'] == self.climbing[self.currs['vdir'] + '_path'][self.currs['index']]:
				print('acertou mano')
				self.currs['index'] += 1
				self.move_correct()
			else:
				print('errou mano')
				self.currs['num_errors'] += 1
				self.move_incorret()

		button = self.grid.itemAtPosition(new_row, new_col)
		if button is None:
			return

		button.widget().setFocus()
		if self.coord['current_move'] == self.coord['previous_move']: # error
			button.widget().setStyleSheet(config.HOVER_FOCUS_DISABLED)
		else:
			button.widget().setStyleSheet(config.HOVER_FOCUS_ENABLED)

	def move_incorret(self):
		self.sound.play(self.sound.UNMATCH, 1.0)
		self.coord['current_move'] = self.coord['previous_move']
		self.coord['last_correct'] = self.coord['previous_move']

	def move_correct(self):
		self.coord['last_correct'] = self.coord['current_move']
		self.grid.itemAtPosition(self.coord['previous_move'][0], 
					self.coord['previous_move'][1]).widget().unset_icon()
		if self.currs['vdir'] == 'up':
			icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_right') + '.png'
			if self.corner_pair[0] == self.coord['corner_top_left']:
				icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_left') + '.png'
			self.grid.itemAtPosition(self.coord['current_move'][0], 
						self.coord['current_move'][1]).widget().set_icon(icon)
			if self.coord['current_move'] == self.corner_pair[0]:
				self.win()
			else:
				self.sound.play(self.sound.MATCH, 1.5)
		else:
			icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_right') + '.png'
			if self.corner_pair[0] == self.coord['corner_bottom_left']:
				icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_left') + '.png'
			self.grid.itemAtPosition(self.coord['current_move'][0], 
						self.coord['current_move'][1]).widget().set_icon(icon)
			if self.coord['current_move'] == self.corner_pair[1]:
				self.win()
			else:
				self.sound.play(self.sound.MATCH, 1.5)
if __name__=='__main__':
	app = QtWidgets.QApplication(sys.argv)
	window = Board()
	window.move(300,50)
	window.setWindowTitle(config.WINDOW_TITLE)
	window.show()
	sys.exit(app.exec_())
### EOF ###
