import os
import numpy as np

global num_big
num_big = 1000
global num_sml
num_sml = 1e-6


# pointnet normalization
def pointnet_norm(data):
    centroid = np.mean(data, axis=0)
    data = data - centroid
    m = np.max(np.sqrt(np.sum(data ** 2, axis=1)))
    data = data / m
    return data


def standardization(data):
    mean = np.mean(data, axis=0)
    sigma = np.std(data, axis=0)
    return (data - mean) / (sigma + 1e-8)


def array2samples_distance(array1, array2):
    num_point, num_features = array1.shape
    num_point1 = array2.shape[0]
    expanded_array1 = np.tile(array1, (num_point1, 1))
    expanded_array2 = np.reshape(
        np.tile(np.expand_dims(array2, 1),
                (1, num_point, 1)),
        (-1, num_features))
    distances = np.linalg.norm(expanded_array1 - expanded_array2, axis=1)
    distances = np.reshape(distances, (num_point1, num_point))
    distances = np.min(distances, axis=1)
    distances = np.mean(distances)
    return distances


def chamfer_distance_numpy(array1, array2):
    av_dist1 = array2samples_distance(array1, array2)
    av_dist2 = array2samples_distance(array2, array1)
    dist = (av_dist1 + av_dist2)
    return dist


def distance_calculate(organ_1, organ_2, center1, center2):
    # chamfer distance
    cost1 = chamfer_distance_numpy(organ_1, organ_2)
    # central point distance
    cost2 = np.linalg.norm(np.mean(organ_2, 0) - np.mean(organ_1, 0))
    # relative distance
    cost3_1 = np.sum(np.linalg.norm(organ_1 - center1, axis=1)) / organ_1.shape[0]
    cost3_2 = np.sum(np.linalg.norm(organ_2 - center2, axis=1)) / organ_2.shape[0]
    cost3 = abs(cost3_1 - cost3_2)
    return 0.7 * cost1 + 0.1 * cost2 + 0.2 * cost3


def build_matrix(pc_bf, pc_af, eval=False):
    bf_class = int(np.max(pc_bf[:, -1])) + 1
    af_class = int(np.max(pc_af[:, -1])) + 1
    bf_central = np.mean(pc_bf[:, :3], axis=0)
    af_central = np.mean(pc_af[:, :3], axis=0)
    cost_array = np.zeros((af_class, bf_class))
    for class_af in range(af_class):
        for class_bf in range(bf_class):
            bf_idx = np.where(pc_bf[:, -1] == class_bf)[0]
            af_idx = np.where(pc_af[:, -1] == class_af)[0]
            bf_curclass = pc_bf[bf_idx, :3]
            af_curclass = pc_af[af_idx, :3]
            if bf_curclass.shape[0] == 0 or af_curclass.shape[0] == 0:
                cost_array[class_af, class_bf] = num_big
            else:
                if eval:
                    cd = 0
                else:
                    cd = chamfer_distance_numpy(bf_curclass[:, :3], af_curclass[:, :3])
                bf_curcent = np.mean(bf_curclass, axis=0)
                af_curcent = np.mean(af_curclass, axis=0)
                af_central_l2 = np.linalg.norm(bf_curcent - af_curcent)
                if eval:
                    af_central_dis = 0
                else:
                    bf_central_dis = np.sum(np.linalg.norm(bf_curclass - bf_central, axis=1)) / len(bf_idx)
                    af_central_dis = np.sum(np.linalg.norm(af_curclass - af_central, axis=1)) / len(af_idx)
                    af_central_dis = abs(bf_central_dis - af_central_dis)
                cost_array[class_af, class_bf] = 0.7 * cd + 0.1 * af_central_l2 + 0.2 * af_central_dis
    return cost_array


def extend_matrix(matrix):
    (m, n) = matrix.shape
    B = np.ones((m, m)) * num_big
    C = np.ones((n, n)) * num_big
    D = np.ones((n, m)) * num_sml
    for rowB in range(m):
        B[rowB, rowB] = 0.9 * np.min(matrix[rowB, :])
        # B[rowB, rowB] = np.min(matrix[rowB, :])
    for colC in range(n):
        C[colC, colC] = 0.9 * np.min(matrix[:, colC])
        # C[colC, colC] = np.min(matrix[:, colC])
    for rB in range(m):
        if np.max(matrix[rB, :]) == np.min(matrix[rB, :]):
            B[rB, rB] = num_sml
    for cC in range(n):
        if np.max(matrix[:, cC]) == np.min(matrix[:, cC]):
            C[cC, cC] = num_sml
    ex_matrix = np.vstack((np.hstack((matrix, B)), np.hstack((C, D))))
    return ex_matrix


def extend_matrix_for_evaluation(matrix):
    (m, n) = matrix.shape
    B = np.ones((m, m)) * num_big
    C = np.ones((n, n)) * num_big
    D = np.ones((n, m)) * num_sml
    for rowB in range(m):
        B[rowB, rowB] = num_sml
    for colC in range(n):
        C[colC, colC] = num_sml
    for rB in range(m):
        if np.max(matrix[rB, :]) == np.min(matrix[rB, :]):
            B[rB, rB] = num_sml
    for cC in range(n):
        if np.max(matrix[:, cC]) == np.min(matrix[:, cC]):
            C[cC, cC] = num_sml
    ex_matrix = np.vstack((np.hstack((matrix, B)), np.hstack((C, D))))
    return ex_matrix


def rank_files(files):
    n = len(files)
    for i in range(n):
        for j in range(n - i - 1):
            if int(files[j].split('_')[0]) > int(files[j + 1].split('_')[0]):
                files[j], files[j + 1] = files[j + 1], files[j]
    return files


def label_refresh(raw_lab, ds_new_lab, ds_old_lab):
    new_lab = np.ones((raw_lab.shape[0], 1)) * (-1)
    for i in np.unique(ds_old_lab):
        index = np.where(ds_old_lab == i)[0]
        assert len(np.unique(ds_new_lab[index])) == 1
        new_lab[np.where(raw_lab == i)] = ds_new_lab[index][0]
    assert -1 not in new_lab
    return new_lab


def find_start(files):
    start_index = [0]
    for start_id in range(1, len(files)):
        if files[start_id].split('_')[2] != files[start_id - 1].split('_')[2] or files[start_id].split('_')[3] != \
                files[start_id - 1].split('_')[3]:
            start_index.append(start_id)
    return start_index


def assign_new_label(init_label, old_label, match_index, start_lab):
    pseudo_lab = np.ones_like(old_label) * (-1)
    next_start = max(max(init_label), start_lab)
    for i in range(len(match_index)):
        if i in old_label:
            if match_index[i] > np.max(init_label):
                next_start = next_start + 1
                pseudo_lab[np.where(old_label == i)[0]] = next_start
            else:
                pseudo_lab[np.where(old_label == i)[0]] = match_index[i]
    assert -1 not in pseudo_lab
    return next_start, pseudo_lab




