#!/usr/bin/env python3
# https://stackoverflow.com/questions/20856518/navigate-between-widgets-using-arrows-in-qt
#
# author: feb 2019
# Cassio Batista - cassio.batista.13@gmail.com

import os

DEGUB = False
PT_BR = False

RESOURCES_DIR  = os.path.join('.', 'res')
SOUNDS_DIR     = os.path.join(RESOURCES_DIR, 'sounds')
ARROW_ICON_DIR = os.path.join(RESOURCES_DIR, 'arrows')
LINES_ICON_DIR = os.path.join(RESOURCES_DIR, 'lines')
CLIMB_ICON_DIR = os.path.join(RESOURCES_DIR, 'climber')

ARDUINO_USED     = False
ARDUINO_PORT     = '/dev/ttyACM1'
ARDUINO_BAUDRATE = 9600
ARDUINO_MSG      = '@'

SOUND_USED       = True

BUTTON_SIZE = 85  # NOTE: pixels?
ICON_SIZE   = 75  # NOTE: pixels?
BOARD_DIM   = 5

assert BUTTON_SIZE > 0, \
			u'o tamanho do botão deve ser um valor positivo' if PT_BR else \
			u'button size must be a positive value'
assert ICON_SIZE > 0, \
			u'o tamanho do ícone deve ser um valor positivo' if PT_BR else \
			u'icon size must be a positive value'
assert BUTTON_SIZE > ICON_SIZE, \
			u'o tamanho do botão deve ser maior que o do ícone' if PT_BR else \
			u'button size must be greater than icon size' 
assert BOARD_DIM > 0, \
			u'as dimensões do tabuleiro devem ser positivas, trouxa' if PT_BR else \
			u'board dimensions must be positive, asshole' 
assert BOARD_DIM % 2 == 1, \
			u'as dimensões devem ser ímpares, retardado' if PT_BR else \
			u'board dimensions must be odd, dumbass'

HOVER_FOCUS_BG_COLOUR = \
	'QPushButton::focus { '    + \
	'    background: %s; '     + \
	'    color: white; '       + \
	'}'

HOVER_FOCUS_IDLE     = HOVER_FOCUS_BG_COLOUR % 'grey'
HOVER_FOCUS_DISABLED = HOVER_FOCUS_BG_COLOUR % 'red'
HOVER_FOCUS_ENABLED  = HOVER_FOCUS_BG_COLOUR % 'green'

WIN_MSG = \
	u'Parabéns, você completou o módulo \'%s path\'!' if PT_BR else \
	u'Congratulations, you finished the %s path!'

WINDOW_TITLE = \
	u'Joguinho em Python 3!' if PT_BR else \
	u'Little Game in Python 3!'

MOUSE_ERROR_MSG = \
	u'Por favor, ao invés de utilizar o mouse, utilize somente o teclado.' if PT_BR else \
	u'Please, do not use the mouse, use only the keyboard instead.'

INFO = WINDOW_TITLE + '<br>' \
	u'<br>' + \
	(u'Autor(es):' if PT_BR else u'Author(s):') + \
	u'<br>' + \
	u'Cassio Trindade Batista' + \
	u'<br><br>' + \
	(u'Contato:' if PT_BR else u'Contact:') + \
	u'<br>' + \
	u'<a href=mailto:cassio.batista.13@gmail.com>cassio.batista.13@gmail.com</a>' + \
	u'<br><br>' + \
	u'Copyleft 2019' + \
	u'<br>' + \
	(u'Lab de Visualização, Interação e Sistemas Inteligentes' if PT_BR else \
	u'Visualization, Interaction and Intelligent Systems Lab') + \
	u'<br>' + \
	(u'Instituto de Ciências Exatas e Naturais' if PT_BR else \
	u'Institute of Exact and Natural Sciences') + \
	u'<br>' + \
	(u'Universidade Federal do Pará' if PT_BR else \
	u'Federal University of Pará') + \
	u'<br>' + \
	(u'Belém, Brasil' if PT_BR else u'Belém, Brazil')

HELP_MSG = WINDOW_TITLE  + '<br>' \
	'<br>' + \
	'<b>Ctrl+L</b>:  ' + (u'calcular caminhos' if PT_BR else u'load paths') + \
	'<br>' + \
	'<b>Ctrl+1</b>: ' + (u'desenhar caminho para escalada' if PT_BR else u'draw path to climb up') + \
	'<br>' + \
	'<b>Ctrl+2</b>: ' + (u'desenhar caminho para descida' if PT_BR else u'draw path to climb down') + \
	'<br>' + \
	'<b>Ctrl+R</b>: ' + (u'reset board' if PT_BR else u'restaurar interface') + \
	'<br>' + \
	'<b>Ctrl+P</b>: ' + (u'começar o jogo' if PT_BR else u'start game') + \
	'<br>' + \
	'<b>Ctrl+Q</b>: ' + (u'fechar interface' if PT_BR else u'close gui') + \
	'<br>' + \
	'<b>Ctrl+I</b>:  ' + (u'sobre a aplicação' if PT_BR else u'about app') + \
	'<br>' + \
	'<b>Ctrl+H</b>:  ' + (u'mostrar mensagem de ajuda' if PT_BR else u'show help message')
### EOF ###
