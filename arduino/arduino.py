#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Erick

import time
import serial
import sys

comport = serial.Serial('/dev/ttyACM0', 9600)
comport.write(str.encode('@'))

#VALUE_SERIAL=comport.readline()
#
#print ('\nRetorno da serial: %s' % (VALUE_SERIAL))

#sys.stderr.write("au")

#print("A")

comport.close()
