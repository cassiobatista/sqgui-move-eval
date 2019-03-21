#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

from PyQt5 import QtWidgets, QtGui, QtCore, QtTest
import config

class Card(QtWidgets.QPushButton):
	def __init__(self):
		super(Card, self).__init__()
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

	def unset_icon(self):
		self.setIcon(QtGui.QIcon())

class LightArrow(Card):
	def __init__(self, snd_obj):
		super(LightArrow, self).__init__()
		self.sound = snd_obj
		self.setFixedSize(config.BUTTON_SIZE,config.BUTTON_SIZE)
		self.onVal = False
		self.order = ['red', 'yellow', 'green']

	def is_on(self):
		return self.onVal

	def set_on(self, on):
		if self.onVal == on:
			return
		self.onVal = on
		self.update()

	def restore(self):
		self.order = ['red', 'yellow', 'green']

	def set_bg_colour(self, colour):
		self.setFocus()
		self.setStyleSheet(config.HOVER_FOCUS_BG_COLOUR % colour)

	@QtCore.pyqtSlot()
	def turn_off(self):
		self.set_on(False)

	@QtCore.pyqtSlot()
	def turn_on(self):
		if len(self.order):
			self.colour = self.order.pop(0)
			self.sound.play(self.sound.REG_BEEP, 1.5)
		self.set_on(True)
		self.set_bg_colour(self.colour)

	on = QtCore.pyqtProperty(bool, is_on, set_on)

class LightState(QtCore.QState):
	def __init__(self, light):
		super(LightState, self).__init__()
		self.light = light
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(1000) # duration
		self.timer.setSingleShot(True)

		self.timing = QtCore.QState(self)
		self.timing.entered.connect(self.light.turn_on)
		self.timing.entered.connect(self.timer.start)
		self.timing.exited.connect(self.light.turn_off)
	
		self.done = QtCore.QFinalState(self)

		self.timing.addTransition(self.timer.timeout, self.done)
	
		self.setInitialState(self.timing)
		self.setObjectName('state')
		self.addTransition(self.finished, self)

# https://stackoverflow.com/questions/9840197/subclass-arguments-from-superclass
class LightMachine(QtCore.QStateMachine):
	def __init__(self, parent, state):
		super(LightMachine, self).__init__(parent) 
		self.state = state
		self.addState(self.state)
		self.setInitialState(self.state)

	def start(self, grid):
		QtTest.QTest.qWait(150)
		super(LightMachine, self).start()
		self.state.light.restore()
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				button = grid.itemAtPosition(i,j).widget()
				button.setEnabled(False)

	def stop(self, grid):
		super(LightMachine, self).stop()
		for i in range(1, config.BOARD_DIM+1):
			for j in range(1, config.BOARD_DIM+1):
				button = grid.itemAtPosition(i,j).widget()
				button.setEnabled(True)
### EOF ###
