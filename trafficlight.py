#!/usr/bin/env python3
# Author velociraptor Genjix <aphidia@hotmail.com>
# source: https://github.com/pyside/Examples/blob/master/examples/state-machine/trafficlight.py
# 
# Ported to PyQt5 on Feb 2019 by Cassio Batista <cassio.batista.13@gmail.com>

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class LightWidget(QtWidgets.QPushButton):
	def __init__(self):
		super(LightWidget, self).__init__()
		self.onVal = False
		self.order = ['red', 'yellow', 'green']
		self.setFixedSize(150,150)

	def isOn(self):
		return self.onVal

	def setOn(self, on):
		if self.onVal == on:
			return
		self.onVal = on
		self.update()

	@QtCore.pyqtSlot()
	def turnOff(self):
		self.setOn(False)

	@QtCore.pyqtSlot()
	def turnOn(self):
		if len(self.order):
			self.colour = self.order.pop(0)
		self.setOn(True)
		self.setFocus()
		self.setStyleSheet('QPushButton::focus { background: %s; color: white; }' % self.colour)

	on = QtCore.pyqtProperty(bool, isOn, setOn)

class LightState(QtCore.QState):
	def __init__(self, light):
		super(LightState, self).__init__()
		timer = QtCore.QTimer(self)
		timer.setInterval(1000) # duration
		timer.setSingleShot(True)

		timing = QtCore.QState(self)
		timing.entered.connect(light.turnOn)
		timing.entered.connect(timer.start)
		timing.exited.connect(light.turnOff)
	
		done = QtCore.QFinalState(self)

		# ref.: https://github.com/pyqt/examples/blob/master/animation/moveblocks.py
		timing.addTransition(timer.timeout, done)
	
		self.setInitialState(timing)
		self.setObjectName('state')
		self.addTransition(self.finished, self)

class TrafficLight(QtWidgets.QWidget):
	def __init__(self):
		super(TrafficLight, self).__init__()

		# ref.: https://github.com/pyqt/examples/blob/master/animation/moveblocks.py
		trans = LightWidget()

		hbox = QtWidgets.QHBoxLayout()
		hbox.addWidget(trans)
		vbox = QtWidgets.QVBoxLayout(self)
		vbox.addLayout(hbox)
		vbox.setContentsMargins(0, 0, 0, 0)

		state   = LightState(trans)
		machine = QtCore.QStateMachine(self)
		machine.addState(state)
		machine.setInitialState(state)
		machine.start()

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	widget = TrafficLight()
	widget.move(510, 400)
	widget.show()
	sys.exit(app.exec_())
