#!/usr/bin/env python3
#
# author: apr 2019
# cassio batista - cassio.batista.13@gmail.com

import sys, os

import numpy as np
import matplotlib.pyplot as plt

def is_float(str_num):
	try:
		float(str_num)
		return True
	except ValueError:
		return False

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('passe os parametro')
		sys.exit(1)

	cf = np.zeros((4,4), dtype=np.int16)
	print(cf, end='\n\n')
	d_arr = ['u', 'd', 'l', 'r']
	with open(sys.argv[1], 'r') as f:
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
	print(cf)
	print('%d movements in total' % sum(sum(cf)))

	plt.imshow(cf,cmap=plt.cm.Greys)
	plt.xticks(np.arange(0,4), ['Up', 'Down', 'Left', 'Right'])
	plt.yticks(np.arange(0,4), ['Up', 'Down', 'Left', 'Right'])
	for i in range(4):
		for j in range(4):
			if cf[j][i] > 0:
				if cf[j][i] > 3:
					color = 'white'
				else:
					color = 'black'
				plt.text(i, j, cf[j][i],
							fontsize=18, color=color,
							horizontalalignment='center', 
							verticalalignment='center')
	plt.xlabel('Predicted', fontsize=18)
	plt.ylabel('Actual',    fontsize=18)
	plt.title(sys.argv[1], fontsize=20)
	plt.show()
