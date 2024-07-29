from utils import *
from scipy.optimize import linear_sum_assignment
import time


if __name__ == "__main__":
    t1 = time.time()
    plant_list = ['maize']
    base = os.getcwd()
    for pid in range(len(plant_list)):
        col_path = os.path.join(base, "col", plant_list[pid])
        cost_path = os.path.join(base, "cost", plant_list[pid])
        res_path = os.path.join(os.path.abspath('..'), "data", "tracking_result", plant_list[pid])
        gt_path = os.path.join(os.path.abspath('..'), "data", "original_data", "gt", plant_list[pid])
        if not os.path.exists(col_path):
            os.mkdir(col_path)
        if not os.path.exists(cost_path):
            os.mkdir(cost_path)
        files = os.listdir(gt_path)
        n = len(files)
        files = rank_files(files)

        for i in range(n):
            gt = np.loadtxt(os.path.join(gt_path, files[i]))
            res = np.loadtxt(os.path.join(res_path, files[i]))
            gt_class = int(np.max(gt[:, -1])) + 1
            res_class = int(np.max(res[:, -1])) + 1
            if len(np.unique(gt[:, -1])) != len(np.unique(res[:, -1])):
                print(files[i] + "gt_class:" + str(len(np.unique(gt[:, -1]))) + "res_class:" + str(
                    len(np.unique(res[:, -1]))) + "   Error!")
            cost = build_matrix(gt, res, True)
            final_matrix = extend_matrix_for_evaluation(cost)
            _, col_ind = linear_sum_assignment(final_matrix)
            np.savetxt(os.path.join(col_path, files[i]), col_ind, fmt="%d")
            np.savetxt(os.path.join(cost_path, files[i]), final_matrix, fmt="%.3f", delimiter=" ")
    t2 = time.time()
    print(t2 - t1)
