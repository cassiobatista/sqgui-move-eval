#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

import sys
import os
import numpy as np
import datetime
import time

from PyQt5 import QtWidgets, QtGui, QtCore, QtTest
from serial import Serial

import config
from sound import Sound
from button import Card, LightArrow, LightState, LightMachine

class Time:
	def __init__(self):
		super(Time, self).__init__()
		self._start_total    = None
		self._stop_total     = None
		self._start_specific = None
		self._stop_specific  = None
		self._all_times      = []

	def start_total(self):
		self._start_total = time.time()
	
	def stop_total(self):
		self._stop_total = time.time()

	def start_specific(self):
		self._start_specific = time.time()

	def stop_specific(self):
		self._stop_specific = time.time()
		self._all_times.append('%.3f' % (self._stop_specific - self._start_specific))

	def get_total_time(self):
		return self._stop_total - self._start_total # FIXME

	def get_all_times(self):
		return self._all_times

class Arduino(Serial):
	def __init__(self):
		super(Arduino, self).__init__(config.ARDUINO_PORT, config.ARDUINO_BAUDRATE)
	
	def send(self):
		self.write(str.encode(config.ARDUINO_MSG))

class Board(QtWidgets.QMainWindow):
	def __init__(self, outfile):
		super(Board, self).__init__()
		self.filename = outfile
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

		if os.path.isfile(self.filename):
			print('warning: file "%s" exists and will be erased' % self.filename)
			os.remove(self.filename)

		self.reset_vars()

		if config.ARDUINO_USED:
			self.arduino = Arduino()
		self.sound = Sound()
		self.time  = Time()
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

	def wait(self, duration):
		for tenth in range(duration//10, duration, duration//10):
			QtTest.QTest.qWait(tenth)
			if not self.keep_waiting:
				break
		self.keep_waiting = True
		if self.currs['index'] < config.BOARD_DIM-1:
			QtTest.QTest.qWait(int(tenth*1.0))

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
		self.times[self.currs['vdir']].start_specific() # NOTE start time for mv
		self.wait(2000) # NOTE

	def enable_board(self, flag):
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				button = self.grid.itemAtPosition(i, j).widget()
				button.setEnabled(flag)

	def start_game(self):
		if not self.is_path_set:
			return
		self.enable_board(True)
		if self.currs['vdir'] == 'down':
			self.draw_bottom_path()
		elif self.currs['vdir'] == 'up':
			self.draw_top_path()
		self.times[self.currs['vdir']].start_total()
		while self.currs['index'] < len(self.climbing[self.currs['vdir'] + '_directions']):
			vdir = self.climbing[self.currs['vdir'] + '_directions'][self.currs['index']]
			if vdir == 'u':
				self.currs['machine'] = self.light_machines['up']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_up.png')
			elif vdir == 'l':
				self.currs['machine'] = self.light_machines['left']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_left.png')
			elif vdir == 'r':
				self.currs['machine'] = self.light_machines['right']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_right.png')
			elif vdir == 'd':
				self.currs['machine'] = self.light_machines['down']
				arrow_icon_path = os.path.join(
							config.ARROW_ICON_DIR, 'arrow_down.png')
			self.currs['machine'].start(self.grid)
			QtTest.QTest.qWait(3100)
			self.currs['machine'].stop(self.grid)
			self.handle_kb_move(arrow_icon_path)
		self.currs['machine'].state.light.set_bg_colour('white')
		self.times[self.currs['vdir']].stop_total()
		self.win()

	def reset_vars(self):
		self.is_path_set = False
		self.keep_waiting = True
		self.corner_pair = ()
		self.coord['current_move'] = self.coord['center']
		self.coord['last_correct'] = self.coord['center']
		self.light_machines = { 'up':None, 'down':None, 'left':None, 'right':None }
		self.currs = {
			'vdir' :'up',
			'index':0,
			'machine':None,
			'num_moves' :0,
			'num_errors':0
		}
		self.climbing = {
			'up_path'  :[],
			'down_path':[],
			'up_directions'  :[],
			'down_directions':[]
		}
		self.times = {
			'up':Time(),
			'down':Time()
		}

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
		self.is_path_set = True

	def calc_random_paths(self):
		if self.currs['vdir'] == 'down':
			QtWidgets.QMessageBox.warning(self, u'Warning',
						u'You cannot load new fresh paths ' + 
						u'because you have already completed ' + 
						u'the top path challenge. Press CTRL+P to start.')
			return
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
		self.enable_board(False)

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
		self.enable_board(False)

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

	def print_stats(self):
		print('number of movements:\t', self.currs['num_moves'])
		print('number of errors:\t', self.currs['num_errors'])
		print('number of correct:\t', self.currs['index'])
		print('total time:\t\t', self.times[self.currs['vdir']].get_total_time())
		print('times per movement:', self.times[self.currs['vdir']].get_all_times())
		with open(self.filename, 'a') as f:
			f.write(self.currs['vdir'] + ':\n')
			f.write('  number of movements:\t' + str(self.currs['num_moves'])  + '\n')
			f.write('  number of errors:\t'    + str(self.currs['num_errors']) + '\n')
			f.write('  number of correct:\t'   + str(self.currs['index'])      + '\n')
			f.write('  total time:\t\t'        + str(self.times[self.currs['vdir']].get_total_time()) + '\n')
			f.write('  times per movement:\t'  + ', '.join(self.times[self.currs['vdir']].get_all_times())  + '\n')

	def win(self):
		if self.sound.stream is not None and self.sound.stream.is_active():
			self.sound.stream.stop_stream()
		if self.currs['vdir'] == 'up':
			icon = os.path.join(config.CLIMB_ICON_DIR, 'mountain_top_climber.png')
		else:
			icon = os.path.join(config.CLIMB_ICON_DIR, 'house_camp_climber.png')

		button = self.grid.itemAtPosition(self.coord['current_move'][0], 
					self.coord['current_move'][1]).widget()
		button.set_icon(icon)
		self.sound.play(self.sound.WIN, 1.0)
		reply = QtWidgets.QMessageBox.information(self, u'You did it', 
					config.WIN_MSG % self.currs['vdir'], QtWidgets.QMessageBox.Ok)

		self.print_stats()

		if self.currs['vdir'] == 'down':
			self.sound.close()
			self.close()
		else:
			self.currs['vdir']       = 'down'
			self.currs['index']      = 0
			self.currs['num_moves']  = 0
			self.currs['num_errors'] = 0 
			self.currs['machine']    = None 
			self.coord['current_move'] = self.coord['center']
			self.coord['last_correct'] = self.coord['center']
			self.draw_bottom_path()

	def on_up(self):
		self.move_focus(0, -1)

	def on_down(self):
		self.move_focus(0, +1)

	def on_left(self):
		self.move_focus(-1, 0)

	def on_right(self):
		self.move_focus(+1, 0)

	def move_focus(self, dx, dy):
		self.times[self.currs['vdir']].stop_specific() # NOTE stop time for mv
		self.currs['num_moves'] += 1
		if self.currs['machine'] is not None and self.currs['machine'].flag:
			print('preventing double move')
			self.currs['num_errors'] += 1
			return

		self.currs['machine'].flag = True

		if QtWidgets.qApp.focusWidget() == 0:
			print('OLHA TO retornando aqui amigo')
			return

		idx = self.grid.indexOf(QtWidgets.qApp.focusWidget())
		if idx == -1:
			print('bicho deu -1 bem aqui')
			return

		button = self.grid.itemAtPosition(self.coord['center'][0], 
					self.coord['center'][1]).widget()

		if not button.isEnabled():
			return

		button.unset_icon() # remove icon from central button 

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
			self.keep_waiting = False
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
		if self.currs['vdir'] == 'up':
			icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_right') + '.png'
			if self.corner_pair[0] == self.coord['corner_top_left']:
				icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_up_left') + '.png'
			self.grid.itemAtPosition(self.coord['current_move'][0], 
						self.coord['current_move'][1]).widget().set_icon(icon)
		else:
			icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_right') + '.png'
			if self.corner_pair[1] == self.coord['corner_bottom_left']:
				icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_left') + '.png'
			self.grid.itemAtPosition(self.coord['current_move'][0], 
						self.coord['current_move'][1]).widget().set_icon(icon)

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
			if self.coord['current_move'] != self.corner_pair[0]:
				self.sound.play(self.sound.MATCH, 1.5)
		else:
			icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_right') + '.png'
			if self.corner_pair[1] == self.coord['corner_bottom_left']:
				icon = os.path.join(config.CLIMB_ICON_DIR, 'climb_down_left') + '.png'
			self.grid.itemAtPosition(self.coord['current_move'][0], 
						self.coord['current_move'][1]).widget().set_icon(icon)
			if self.coord['current_move'] != self.corner_pair[1]:
				self.sound.play(self.sound.MATCH, 1.5)

if __name__=='__main__':
	if len(sys.argv) != 2:
		print('usage: (python3) ./%s <out_stat_file>')
		sys.exit(1)
	app = QtWidgets.QApplication(sys.argv)
	window = Board(sys.argv[1])
	window.move(300,50)
	window.setWindowTitle(config.WINDOW_TITLE)
	window.show()
	sys.exit(app.exec_())
### EOF ###
