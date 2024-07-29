import os.path
from functools import partial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pycpd import DeformableRegistration
import numpy as np


def visualize(iteration, error, X, Y, ax, saved_path, label):
    # save_name = os.path.join(saved_path, "8") + "_" + str(iteration) + ".txt"
    # np.savetxt(save_name, np.hstack((Y, label)), fmt="%f %f %f %d", delimiter=" ")
    plt.cla()
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], color='red', label='Target')
    ax.scatter(Y[:, 0], Y[:, 1], Y[:, 2], color='blue', label='Source')
    ax.text2D(0.87, 0.92, 'Iteration: {:d}'.format(
        iteration), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
              fontsize='x-large')
    ax.legend(loc='upper left', fontsize='x-large')
    plt.draw()
    plt.pause(0.1)


def main():
    target_path = r'D:\Zest\汇报\代码\pycpd-master\data\5_maize_control_plant1_D04.txt'
    fish_target = np.loadtxt(target_path)
    X = fish_target[:, :3]
    # X = np.vstack((fish_target, fish_target))

    source_path = r'D:\Zest\汇报\代码\pycpd-master\data\6_maize_control_plant1_D05.txt'
    fish_source = np.loadtxt(source_path)
    Y = fish_source[:, :3]
    label = fish_source[:, -1].reshape(-1, 1)
    # Y = np.vstack((fish_source, fish_source))

    saved_path = r"D:\Tools_llz\reg_middle\reg"

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    callback = partial(visualize, ax=ax, saved_path=saved_path, label=label)

    reg = DeformableRegistration(**{'X': X, 'Y': Y, 'low_rank': False})
    reg.register(callback)
    plt.show()


if __name__ == '__main__':
    main()
