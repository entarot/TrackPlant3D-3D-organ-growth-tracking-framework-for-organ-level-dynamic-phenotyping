import os
import shutil
import time

from scipy.optimize import linear_sum_assignment
from utils import *


def log_string(out_str):
    log_file.write(out_str + '\n')
    log_file.flush()
    print(out_str)


if __name__ == '__main__':
    plant_list = ['maize','sorghum','tobacco','tomato']
    sample_method = '3DEPS'
    base = os.path.abspath('..')
    for pid in range(len(plant_list)):
        path_raw = os.path.join(base, "data", "original_data", "raw", plant_list[pid])
        sampled_path = os.path.join(base, "data", "sampled_data", sample_method, plant_list[pid])
        path_reg = os.path.join(base, "data", "registration_result", plant_list[pid])
        save_path = os.path.join(base, "data", "tracking_result", plant_list[pid])
        col_path = os.path.join(os.getcwd(), "col")
        cost_path = os.path.join(os.getcwd(), "cost")
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        if not os.path.exists(col_path):
            os.mkdir(col_path)
        if not os.path.exists(cost_path):
            os.mkdir(cost_path)

        log_path = os.path.join(os.getcwd())
        log_file = open(os.path.join(log_path, plant_list[pid] + "_log.txt"), "w")

        files = os.listdir(sampled_path)
        files = rank_files(files)
        n = len(files)
        start_index = find_start(files)

        for i in range(n):
            if i in start_index:
                start_label = 0
                d_before = np.loadtxt(os.path.join(sampled_path, files[i]))
                label_match = d_before[:, 3].reshape(-1, 1)
                shutil.copy(os.path.join(path_raw, files[i]), os.path.join(save_path, files[i]))
            else:
                # log_string("--------Plant %s Tracking Start--------" % files[i])

                d_before = np.loadtxt(os.path.join(sampled_path, files[i - 1]))
                d_before = np.hstack((d_before[:, 0:3], label_match))
                d_after = np.loadtxt(os.path.join(path_reg, files[i]))
                bf_class = int(np.max(d_before[:, -1])) + 1
                af_class = int(np.max(d_after[:, -1])) + 1
                cost_matrix = build_matrix(d_before, d_after)
                final_matrix = extend_matrix(cost_matrix)
                _, col_ind = linear_sum_assignment(final_matrix)
                before_label = d_before[:, -1].reshape(-1, 1)
                after_label = d_after[:, -1].reshape(-1, 1)
                start_label, pseudo_label = assign_new_label(before_label, after_label, col_ind, start_label)
                match_res = np.loadtxt(os.path.join(sampled_path, files[i]))[:, :3]
                raw_data = np.loadtxt(os.path.join(path_raw, files[i]))
                raw_label = raw_data[:, -1].reshape(-1, 1)
                new_label = label_refresh(raw_label, pseudo_label, after_label)
                label_match = pseudo_label
                np.savetxt(os.path.join(save_path, files[i]), np.hstack((raw_data[:, :3], new_label)), fmt="%f %f %f %d")
                np.savetxt(os.path.join(cost_path, files[i]), final_matrix, fmt="%.1f", delimiter=" ")
                np.savetxt(os.path.join(col_path, files[i]), col_ind, fmt="%d")
