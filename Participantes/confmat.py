#!/usr/bin/env python3
#
# author: apr 2019
# cassio batista - cassio.batista.13@gmail.com

import sys, os
import glob

import numpy as np
import matplotlib.pyplot as plt

def is_float(str_num):
	try:
		float(str_num)
		return True
	except ValueError:
		return False

def calc_confusion_matrix(cf, f):
	for line in f:
		split = line.split()
		if len(split) > 2 and is_float(split[0]):
			actual  = d_arr.index(split[2].strip('()'))
			if split[1] == 'correct':
				predict = d_arr.index(split[2].strip('()'))
			elif split[1] == 'wrong':
				predict = d_arr.index(split[4].strip('()')[0])
			else:
				continue # FIXME dup?
			cf[actual][predict] += 1

def plot_cf_from_file(cf, filename):
	with open(filename, 'r') as f:
		calc_confusion_matrix(cf, f)
	return cf

def plot_cf_overview(cf):
	for f_txt in glob.glob('*.txt'):
		with open(f_txt, 'r') as f:
			calc_confusion_matrix(cf, f)
	return cf

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print('passe um parâmetro ou não passe nada')
		sys.exit(1)

	cf = np.zeros((4,4), dtype=np.int16)
	d_arr = ['u', 'd', 'l', 'r']
	print(cf, end='\n\n')
	if len(sys.argv) == 2:
		if os.path.isfile(sys.argv[1]):
			cf = plot_cf_from_file(cf, sys.argv[1])
		else:
			print('error: "%s" is not a valid file' % sys.argv[1])
			sys.exit(2)
	else:
		cf = plot_cf_overview(cf)
	print(cf, '%d movements in total' % sum(sum(cf)))

	plt.imshow(cf,cmap=plt.cm.Greys)
	plt.xticks(np.arange(0,4), ['Cima', 'Baixo', 'Esquerda', 'Direita'])
	plt.yticks(np.arange(0,4), ['Cima', 'Baixo', 'Esquerda', 'Direita'])
	for i in range(4):
		for j in range(4):
			if cf[j][i] > 0:
				print(len(glob.glob('*.txt')))
				if len(sys.argv) == 2 and cf[j][i] > 3:
					color = 'white'
				elif cf[j][i] > 4*len(glob.glob('*.txt'))//2:
					color = 'white'
				else:
					color = 'black'
				plt.text(i, j, cf[j][i],
							fontsize=18, color=color,
							horizontalalignment='center', 
							verticalalignment='center')
	plt.xlabel('Valor previsto', fontsize=18)
	plt.ylabel('Valor real',     fontsize=18)
	if len(sys.argv) == 2:
		plt.title(sys.argv[1], fontsize=20)
	else:
		plt.title('todo mundo', fontsize=20)
	plt.show()
