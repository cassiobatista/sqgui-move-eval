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

BUTTON_SIZE = 100 # NOTE: pixels?
ICON_SIZE   = 90 # NOTE: pixels?
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

HOVER_FOCUS = \
	'QPushButton::focus { '   + \
	'    background: blue; ' + \
	'    color: white; '      + \
	'}'

WIN_MSG = \
	u'Parabéns, você conseguiu!' if PT_BR else \
	u'Congratulations, you did it!'

WINDOW_TITLE = \
	u'Joguingo em Python 3!' if PT_BR else \
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

