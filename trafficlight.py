#!/usr/bin/env python3
# Author velociraptor Genjix <aphidia@hotmail.com>
# source: https://github.com/pyside/Examples/blob/master/examples/state-machine/trafficlight.py
# 
# Ported to PyQt5 on Feb 2019 by Cassio Batista <cassio.batista.13@gmail.com>

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class LightWidget(QtWidgets.QPushButton):
	def __init__(self, colour):
		super(LightWidget, self).__init__()
		self.colour = colour
		self.onVal  = False
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
		self.setOn(True)
		if self.colour is not None:
			self.setFocus()
			self.setStyleSheet('QPushButton::focus { background: %s; color: white; }' % self.colour)

	#def paintEvent(self, e):
	#	if not self.onVal:
	#		return
	#	painter = QtGui.QPainter(self)
	#	painter.setRenderHint(QtGui.QPainter.Antialiasing)
	#	painter.setBrush(self.colour)
	#	painter.drawEllipse(0, 0, self.width(), self.height())

	on = QtCore.pyqtProperty(bool, isOn, setOn)

class TrafficLight(QtWidgets.QWidget):
	def __init__(self):
		super(TrafficLight, self).__init__()

		self.trans  = LightWidget(None) #QtCore.Qt.transparent)
		self.red    = LightWidget('red') #QtCore.Qt.red)
		self.yellow = LightWidget('yellow') #QtCore.Qt.yellow)
		self.green  = LightWidget('green') #QtCore.Qt.green)

		self.hbox = QtWidgets.QHBoxLayout()
		self.hbox.addWidget(self.trans)
		self.hbox.addWidget(self.red)
		self.hbox.addWidget(self.yellow)
		self.hbox.addWidget(self.green)

		vbox = QtWidgets.QVBoxLayout(self)
		vbox.addLayout(self.hbox)
		vbox.setContentsMargins(0, 0, 0, 0)

		t2r = self.createLightState(self.trans,  500)
		r2y = self.createLightState(self.red,    500)
		y2g = self.createLightState(self.yellow, 500)
		g2t = self.createLightState(self.green,  500)

		t2r.setObjectName('t2r')
		r2y.setObjectName('r2y')
		y2g.setObjectName('y2g')
		g2t.setObjectName('g2t')

		# ref.: https://github.com/pyqt/examples/blob/master/animation/moveblocks.py
		t2r.addTransition(t2r.finished, r2y)
		r2y.addTransition(r2y.finished, y2g)
		y2g.addTransition(y2g.finished, g2t)
		g2t.addTransition(g2t.finished, t2r)

		machine = QtCore.QStateMachine(self)
		machine.addState(t2r)
		machine.addState(r2y)
		machine.addState(y2g)
		machine.addState(g2t)
		machine.setInitialState(t2r)
		machine.start()

	def createLightState(self, light, duration, parent=None):
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


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	widget = TrafficLight()
	#widget.resize(110, 300)
	widget.move(510, 400)
	widget.show()
	sys.exit(app.exec_())
