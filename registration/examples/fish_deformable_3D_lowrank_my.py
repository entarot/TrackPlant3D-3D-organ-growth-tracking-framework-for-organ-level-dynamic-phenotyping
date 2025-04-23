import os
import time
from functools import partial
from registration.pycpd import DeformableRegistration
from utils import *


def visualize(iteration, error, X, Y, saved_path, label):
    np.savetxt(saved_path, np.hstack((Y, label)), fmt="%f %f %f %d", delimiter=" ")


def main():
    plant_list = ['maize','sorghum','tobacco','tomato']
    sample_method = '3DEPS'
    total_start_time = time.time()
    for pid in range(len(plant_list)):
        start_time = time.time()
        base = os.path.dirname(os.path.dirname(os.getcwd()))
        data_path = os.path.join(base, "data", "sampled_data", sample_method, plant_list[pid])
        save_path = os.path.join(base, "data", "registration_result", plant_list[pid])
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        files = os.listdir(data_path)
        n = len(files)
        files = rank_files(files)
        # print(files)
        for j in range(n - 1):
            if (files[j].split('_')[3] == files[j + 1].split('_')[3]) & (
                    files[j].split('_')[2] == files[j + 1].split('_')[2]):
                target = np.loadtxt(os.path.join(data_path, files[j]))
                X = target[:, :3]
                source = np.loadtxt(os.path.join(data_path, files[j + 1]))
                label = source[:, -1].reshape(-1, 1)
                Y = source[:, :3]
                saved_path = os.path.join(save_path, files[j + 1])
                callback = partial(visualize, label=label, saved_path=saved_path)
                reg = DeformableRegistration(**{'X': X, 'Y': Y, 'low_rank': False})
                reg.register(callback)
        end_time = time.time()
        print(end_time - start_time)

    total_end_time = time.time()
    print(total_end_time-total_start_time)


if __name__ == '__main__':
    main()
