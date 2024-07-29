from functools import partial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from registration.pycpd import DeformableRegistration
import numpy as np


def visualize(iteration, error, X, Y, ax,lab):

    plt.cla()
    ax.scatter(X[:, 0],  X[:, 1], X[:, 2], color='red', label='Target')
    ax.scatter(Y[:, 0],  Y[:, 1], Y[:, 2], color='blue', label='Source')
    ax.text2D(1, 1, 'Iteration: {:d}'.format(
        iteration), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize='x-large')
    ax.legend(loc='upper left', fontsize='x-large')
    plt.draw()
    plt.pause(0.001)

    np.savetxt(r'C:\Users\llz\Desktop\7_reg.txt', np.hstack((Y, lab)), fmt="%f %f %f %d", delimiter=" ")


def main():
    fish_target = np.loadtxt(r'D:\Tools_llz\TrackII_resultII\不同配准顺序测试\2\gt_normlization\8_maize_control_plant1_D07.txt')[:, :3]
    X = fish_target
    fish_source = np.loadtxt(r'C:\Users\llz\Desktop\7_maize_control_plant1_D06.txt')
    Y = fish_source[:,:3]
    label = fish_source[:,-1].reshape(-1,1)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    callback = partial(visualize, ax=ax,lab=label)

    reg = DeformableRegistration(**{'X': Y, 'Y': X, 'low_rank': True})
    reg.register(callback)
    plt.show()


if __name__ == '__main__':
    main()
