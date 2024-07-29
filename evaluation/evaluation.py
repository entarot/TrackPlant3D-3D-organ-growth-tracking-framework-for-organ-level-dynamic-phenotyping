import time
from utils import *


def log_string(out_str):
    log_file.write(out_str + '\n')
    log_file.flush()
    print(out_str)


if __name__ == "__main__":
    t1 = time.time()
    plant_list = ['maize']
    base = os.getcwd()
    for pid in range(len(plant_list)):
        col_path = os.path.join(base, "col", plant_list[pid])
        res_path = os.path.join(os.path.abspath('..'), "data", "tracking_result", plant_list[pid])
        gt_path = os.path.join(os.path.abspath('..'), "data", "original_data", "gt", plant_list[pid])
        # LTTA metric
        total_instance = 0
        seq_total_instance = 0
        true_matchI = 0
        seq_true_matchI = 0
        # STTA metric
        STTA = True
        true_matchII = 0
        seq_true_matchII = 0
        id_switch = 0
        seq_id_switch = 0

        log_save = os.getcwd()
        log_file = open(os.path.join(log_save, plant_list[pid] + "_evaluation.txt"), "w")

        files = os.listdir(col_path)
        num_files = len(files)
        files = rank_files(files)
        start = find_start(files)

        for i in range(num_files):
            if i not in start:
                gt_data = np.loadtxt(os.path.join(gt_path, files[i]))
                gt_class = int(np.max(gt_data[:, -1])) + 1
                bf_gt_data = np.loadtxt(os.path.join(gt_path, files[i - 1]))
                bf_gt_class = int(np.max(bf_gt_data[:, -1])) + 1
                cur_data = np.loadtxt(os.path.join(res_path, files[i]))
                cur_class = int(np.max(cur_data[:, -1])) + 1
                total_instance = total_instance + len(np.unique(cur_data[:, -1]))
                seq_total_instance = seq_total_instance + len(np.unique(cur_data[:, -1]))

                # 视为错误
                for mat in range(gt_class):
                    if mat in cur_data[:, -1]:
                        if np.sum((gt_data[:, -1] == mat)) == np.sum(cur_data[:, -1] == mat):
                            true_matchI += 1
                            seq_true_matchI += 1
                # 不视为错误
                # for mat in range(bf_gt_class):
                #     if mat in cur_data[:, -1]:
                #         if np.sum((gt_data[:, -1] == mat)) == np.sum(cur_data[:, -1] == mat):
                #             true_matchI += 1
                #             seq_true_matchI = seq_true_matchI + 1
                # for mat in range(bf_gt_class, gt_class):
                #     if mat in cur_data[:, -1]:
                #         for add in range(bf_gt_class, gt_class):
                #             if np.sum((gt_data[:, -1] == add)) == np.sum(cur_data[:, -1] == mat):
                #                 true_matchI += 1
                #                 seq_true_matchI = seq_true_matchI + 1
                if STTA:
                    bf_data = np.loadtxt(os.path.join(res_path, files[i - 1]))
                    bf_class = int(np.max(bf_data[:, -1])) + 1
                    cur_col = np.loadtxt(os.path.join(col_path, files[i])).reshape(-1, 1)
                    bf_col = np.loadtxt(os.path.join(col_path, files[i - 1])).reshape(-1, 1)
                    # Short Term Tracking Accuracy
                    for ins in range(bf_class):
                        if ins in bf_data[:, -1] and ins in cur_data[:, -1]:
                            if cur_col[ins, 0] == bf_col[ins, 0]:
                                true_matchII += 1
                                seq_true_matchII += 1
                            else:
                                id_switch += 1
                                seq_id_switch += 1
                    for ins in range(bf_class, cur_class):
                        if ins in cur_data[:, -1]:
                            if cur_col[ins, 0] >= bf_gt_class:
                                true_matchII += 1
                                seq_true_matchII += 1
                            else:
                                id_switch += 1
                                seq_id_switch += 1
                    # print(files[i])
                    # print(seq_id_switch)

            if i < num_files - 1:
                if files[i].split("_")[3] != files[i + 1].split("_")[3] or files[i].split('_')[2] != \
                        files[i + 1].split('_')[2]:
                    log_string(files[i].split('.')[0] + "  Sequence Tracking Result:")
                    log_string("total_instance=%d" % seq_total_instance)
                    log_string("true_matchI=%d" % seq_true_matchI)
                    if STTA:
                        log_string("true_matchII=%d" % seq_true_matchII)
                        log_string("id switch =%d" % seq_id_switch)
                    seq_total_instance = 0
                    seq_true_matchI = 0
                    seq_true_matchII = 0
                    seq_id_switch = 0
                    log_string("--------------------------------")
            elif i == num_files - 1:
                log_string(files[i].split('.')[0] + "  Sequence Tracking Result:")
                log_string("total_instance=%d" % seq_total_instance)
                log_string("true_matchI=%d" % seq_true_matchI)
                if STTA:
                    log_string("true_matchII=%d" % seq_true_matchII)
                    log_string("id switch =%d" % seq_id_switch)
                seq_total_instance = 0
                seq_true_matchI = 0
                seq_true_matchII = 0
                seq_id_switch = 0
                log_string("----------Tracking End----------")

        acc1 = float(true_matchI / total_instance)
        log_string("total_instance=%d" % total_instance)
        log_string("true_matchI=%d" % true_matchI)
        log_string("AccuracyI =%f" % acc1)
        if STTA:
            acc2 = float(true_matchII / total_instance)
            log_string("true_matchII=%d" % true_matchII)
            log_string("AccuracyII =%f" % acc2)
            log_string("id switch =%d" % id_switch)
    t2 = time.time()
    print(t2 - t1)
