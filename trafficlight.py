#!/usr/bin/env python3
# Author velociraptor Genjix <aphidia@hotmail.com>
# source: https://github.com/pyside/Examples/blob/master/examples/state-machine/trafficlight.py
# 
# Ported to PyQt5 on Feb 2019 by Cassio Batista <cassio.batista.13@gmail.com>

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class LightWidget(QtWidgets.QWidget):
	def __init__(self, colour):
		super(LightWidget, self).__init__()
		self.colour = colour
		self.onVal  = False

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
		self.setOn(True)

	def paintEvent(self, e):
		if not self.onVal:
			return
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.setBrush(self.colour)
		painter.drawEllipse(0, 0, self.width(), self.height())

	on = QtCore.pyqtProperty(bool, isOn, setOn)

class TrafficLightWidget(QtWidgets.QWidget):
	def __init__(self):
		super(TrafficLightWidget, self).__init__()
		self.redLight    = LightWidget(QtCore.Qt.red)
		self.yellowLight = LightWidget(QtCore.Qt.yellow)
		self.greenLight  = LightWidget(QtCore.Qt.green)

		vbox = QtWidgets.QVBoxLayout(self)
		vbox.addWidget(self.redLight)
		vbox.addWidget(self.yellowLight)
		vbox.addWidget(self.greenLight)

		pal = QtGui.QPalette()
		pal.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
		self.setPalette(pal)
		self.setAutoFillBackground(True)

def createLightState(light, duration, parent=None):
	lightState = QtCore.QState(parent)

	timer = QtCore.QTimer(lightState)
	timer.setInterval(duration)
	timer.setSingleShot(True)

	timing = QtCore.QState(lightState)
	timing.entered.connect(light.turnOn)
	timing.entered.connect(timer.start)
	timing.exited.connect(light.turnOff)

	done = QtCore.QFinalState(lightState)

	# ref.: https://github.com/pyqt/examples/blob/master/animation/moveblocks.py
	timing.addTransition(timer.timeout, done)

	lightState.setInitialState(timing)
	return lightState

class TrafficLight(QtWidgets.QWidget):
	def __init__(self):
		super(TrafficLight, self).__init__()
		vbox = QtWidgets.QVBoxLayout(self)
		widget = TrafficLightWidget()
		vbox.addWidget(widget)
		vbox.setContentsMargins(0, 0, 0, 0)

		machine = QtCore.QStateMachine(self)

		redGoingYellow   = createLightState(widget.yellowLight, 1000)
		yellowGoingGreen = createLightState(widget.redLight,    1000)
		greenGoingYellow = createLightState(widget.yellowLight, 1000)
		yellowGoingRed   = createLightState(widget.greenLight,  1000)

		redGoingYellow.setObjectName('redGoingYellow')
		yellowGoingGreen.setObjectName('redGoingYellow')
		greenGoingYellow.setObjectName('redGoingYellow')
		yellowGoingRed.setObjectName('redGoingYellow')

		# ref.: https://github.com/pyqt/examples/blob/master/animation/moveblocks.py
		redGoingYellow.addTransition  (redGoingYellow.finished, yellowGoingGreen)
		yellowGoingGreen.addTransition(yellowGoingGreen.finished, greenGoingYellow)
		greenGoingYellow.addTransition(greenGoingYellow.finished, yellowGoingRed)
		yellowGoingRed.addTransition  (yellowGoingRed.finished, redGoingYellow)

		machine.addState(redGoingYellow)
		machine.addState(yellowGoingGreen)
		machine.addState(greenGoingYellow)
		machine.addState(yellowGoingRed)
		machine.setInitialState(redGoingYellow)

		machine.start()

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	widget = TrafficLight()
	widget.resize(110, 300)
	widget.move(510, 400)
	widget.show()
	sys.exit(app.exec_())
