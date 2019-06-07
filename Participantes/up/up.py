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
            actual  = d_arr_actual.index(split[2].strip('()'))
            if split[1] == 'correct':
                predict = d_arr_pred.index(split[2].strip('()'))
            elif split[1] == 'wrong':
                predict = d_arr_pred.index(split[4].strip('()')[0])
            else:
                continue # FIXME dup?
            cf[actual][predict] += 1

def plot_cf_from_file(cf, filename):
    with open(filename, 'r') as f:
        calc_confusion_matrix(cf, f)
    return cf

def plot_cf_overview(cf):
    for f_txt in glob.glob('*.up'):
        with open(f_txt, 'r') as f:
            calc_confusion_matrix(cf, f)
    return cf

# NOTE: 
#   3.5 works good for 40
#   5.0 works good for 80
def normalize(cf):
    for i in range(3):
        for j in range(4):
            cf[i][j] /= 5.0 # see NOTE above

def denormalize(cf):
    for i in range(3):
        for j in range(4):
            cf[i][j] *= 5.0 # see NOTE above

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print('passe um parâmetro ou não passe nada')
        sys.exit(1)

    cf = np.zeros((3,4), dtype=np.float16)
    d_arr_actual = ['u', 'l', 'r']
    d_arr_pred   = ['u', 'd', 'l', 'r']
    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            cf = plot_cf_from_file(cf, sys.argv[1])
        else:
            print('error: "%s" is not a valid file' % sys.argv[1])
            sys.exit(2)
    else:
        cf = plot_cf_overview(cf)
        normalize(cf)
    print(cf, '\n%d movements in total' % sum(sum(cf)), end='\n\n')

    cf2 = np.copy(cf)
    for i in range(3):
        for j in range(4):
            if cf2[i][j] > 4:
                cf2[i][j] = 2.0

    print('##')
    print(cf2)
    print('##')

    plt.imshow(np.array(cf2, dtype=np.int16),cmap=plt.cm.Blues)
    plt.xticks(np.arange(0,4), ['Up', 'Down', 'Left', 'Right'], fontsize=24)
    plt.yticks(np.arange(0,3), ['Up', 'Left', 'Right'], va='center', fontsize=24, rotation=90)
    denormalize(cf)
    for i in range(4):
        for j in range(3):
            if True: #cf[j][i] > 0:
                if len(sys.argv) == 2 and cf[j][i] > 3:
                    color = 'white'
                elif cf[j][i] > 2*len(glob.glob('*.txt'))//2:
                    color = 'white'
                else:
                    color = 'black'
                plt.text(i, j, int(cf[j][i]),
                            fontsize=18, color=color,
                            horizontalalignment='center', 
                            verticalalignment='center')
    print(np.array(cf, dtype=np.int16))
    plt.xlabel('Predicted movement',  fontsize=32)
    plt.ylabel('Actual movement',     fontsize=32)
    #if len(sys.argv) == 2:
    #    plt.title(sys.argv[1], fontsize=20)
    #else:
    #    plt.title('todo mundo', fontsize=20)
    plt.subplots_adjust(top=0.95, bottom=0.10, right=0.975, left=0.100)
    plt.show()
