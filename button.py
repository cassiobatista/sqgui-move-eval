#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

from PyQt5 import QtWidgets, QtGui, QtCore, QtTest
import config

class Card(QtWidgets.QPushButton):
	def __init__(self, blank_icon_path=None):
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

class LightArrow(Card):
	def __init__(self, snd_obj):
		super(LightArrow, self).__init__()
		self.sound = snd_obj
		self.setFixedSize(config.BUTTON_SIZE,config.BUTTON_SIZE)
		self.onVal = False
		self.order = ['red', 'yellow', 'green']
		self.sound.wav = self.sound.REG_BEEP

	def is_on(self):
		return self.onVal

	def set_on(self, on):
		if self.onVal == on:
			return
		self.onVal = on
		self.update()

	def restore(self):
		self.order = ['red', 'yellow', 'green']
		self.sound.wav = self.sound.REG_BEEP

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
			self.sound.play(1.5)
		self.set_on(True)
		self.set_bg_colour(self.colour)

	on = QtCore.pyqtProperty(bool, is_on, set_on)

class LightState(QtCore.QState):
	def __init__(self, light):
		super(LightState, self).__init__()
		self.light = light
		timer = QtCore.QTimer(self)
		timer.setInterval(1000) # duration
		timer.setSingleShot(True)

		timing = QtCore.QState(self)
		timing.entered.connect(self.light.turn_on)
		timing.entered.connect(timer.start)
		timing.exited.connect(self.light.turn_off)
	
		done = QtCore.QFinalState(self)

		timing.addTransition(timer.timeout, done)
	
		self.setInitialState(timing)
		self.setObjectName('state')
		self.addTransition(self.finished, self)

# https://stackoverflow.com/questions/9840197/subclass-arguments-from-superclass
class LightMachine(QtCore.QStateMachine):
	def __init__(self, parent, state):
		super(LightMachine, self).__init__(parent) 
		self.state = state
		self.addState(self.state)
		self.setInitialState(self.state)

	def start(self):
		QtTest.QTest.qWait(200)
		super(LightMachine, self).start()
		self.state.light.restore()
### EOF ###
