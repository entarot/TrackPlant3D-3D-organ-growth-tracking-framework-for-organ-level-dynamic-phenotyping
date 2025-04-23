import os
from os import listdir, path
import shutil
import time
import open3d as o3d
import numpy as np
from utils import pointnet_norm

base = os.path.abspath('..')
plant_list = ['maize','sorghum','tobacco','tomato']

class FarthestSampler:
    def __init__(self):
        pass
    def _calc_distances(self, p0, points):
        return ((p0 - points) ** 2).sum(axis=1)
    def _call__(self, pts, k):
        farthest_pts = np.zeros((k, 4), dtype=np.float32)
        farthest_pts[0] = pts[np.random.randint(len(pts))]
        distances = self._calc_distances(farthest_pts[0,:3], pts[:,:3])
        for i in range(1, k):
            farthest_pts[i] = pts[np.argmax(distances)]
            distances = np.minimum( distances, self._calc_distances(farthest_pts[i,:3], pts[:,:3]))
        return farthest_pts

def edge_separation_of_point_cloud(edge_path, core_path):
    for pid in range(len(plant_list)):
        pc_path = os.path.join(base, "data", "original_data", "raw", plant_list[pid])
        files = os.listdir(pc_path)
        for i in range(len(files)):
            file_name = os.path.join(pc_path, files[i])
            points = np.loadtxt(file_name)
            pcd = o3d.t.geometry.PointCloud(points[:, :3])
            pcd.estimate_normals(max_nn=20)
            boundarys, mask = pcd.compute_boundary_points(radius=10, max_nn=20, angle_threshold=90)
            edge_point_index = mask.numpy()
            core_point_index = ~edge_point_index
            boundarys_points = points[edge_point_index, :]
            core_point = points[core_point_index, :]
            np.savetxt(os.path.join(edge_path, files[i]), boundarys_points, fmt="%f %f %f %d")
            np.savetxt(os.path.join(core_path, files[i]), core_point, fmt="%f %f %f %d")

def merge_edge_and_core(edge_path, core_path, merge_path):
    txt_cs = [f for f in listdir(core_path)
              if f.endswith('.txt') and path.isfile(path.join(core_path, f))]
    txt_es = [f for f in listdir(edge_path)
              if f.endswith('.txt') and path.isfile(path.join(edge_path, f))]
    i = 0
    for txt_c, txt_e in zip(txt_cs, txt_es):
        c_temp = []
        e_temp = []
        end_temp = []
        i = i + 1
        with open(os.path.join(core_path, txt_c), 'r') as f:
            index = []
            lines = f.readlines()
            size_c = len(lines)  # Get the length of the input data
            np.random.seed(1)
            indexs = np.random.randint(0, size_c, 4096,int)
            for index in indexs:
                c_temp.append(lines[index])

        with open(os.path.join(edge_path, txt_e), 'r') as f:
            index = []
            lines = f.readlines()
            size_e = len(lines)
            np.random.seed(i)
            indexs = np.random.randint(0, size_e, 4096, int)

            for index in indexs:
                e_temp.append(lines[index])
        end_temp = c_temp + e_temp
        with open(os.path.join(merge_path, txt_e.split('.')[0] + ".txt"), 'w') as f:
            f.write(''.join(end_temp[0:]))

def downsampling_of_point_cloud(merge_path, downsample_path):
    files = os.listdir(merge_path)
    for i in range(len(files)):
        print(files[i])
        points = np.loadtxt(os.path.join(merge_path, files[i]))
        pcd_array = np.array(points)
        print("pcd_array.shape:", pcd_array.shape)
        sample_count = 256  # Fixed number of points after FPS downsampling
        ratio = 0.5  # proportionality ratio 设置为0.5
        CoreNum = 4096  # Number of core points in merged data
        FPS = FarthestSampler()  #
        center_points = FPS._call__(pcd_array[0:CoreNum, 0:4], sample_count - int(sample_count * ratio))
        edg_points = FPS._call__(pcd_array[CoreNum:, 0:4], int(sample_count * ratio))
        sample_points = np.concatenate((center_points, edg_points), axis=0)  # joint into a new point cloud
        norm_point = pointnet_norm(sample_points[:,:3])
        final_points = np.hstack((norm_point, sample_points[:,-1].reshape(-1,1)))
        # Obtain the file name under the path and remove the suffix
        if not os.path.exists(downsample_path):
            os.mkdir(downsample_path)
        np.savetxt(os.path.join(downsample_path, files[i]), final_points,fmt='%f %f %f %d')

def sort_plant(downsample_path):
    files = os.listdir(downsample_path)
    for i in range(len(files)):
        if 'maize' in files[i]:
            save_path = os.path.join(downsample_path, 'maize')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            shutil.move(os.path.join(downsample_path, files[i]), save_path)
        if 'sorghum' in files[i]:
            save_path = os.path.join(downsample_path, 'sorghum')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            shutil.move(os.path.join(downsample_path, files[i]), save_path)
        if 'tomato' in files[i]:
            save_path = os.path.join(downsample_path, 'tomato')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            shutil.move(os.path.join(downsample_path, files[i]), save_path)
        if 'tobacco' in files[i]:
            save_path = os.path.join(downsample_path, 'tobacco')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            shutil.move(os.path.join(downsample_path, files[i]), save_path)

if __name__ == '__main__':
    edge_save_path = os.path.join(base, "data", "sampled_data", 'edge')
    if not os.path.exists(edge_save_path):
        os.makedirs(edge_save_path)
    core_save_path = os.path.join(base, "data", "sampled_data", 'core')
    if not os.path.exists(core_save_path):
        os.makedirs(core_save_path)
    merge_save_path = os.path.join(base, "data", "sampled_data", 'merge')
    if not os.path.exists(merge_save_path):
        os.makedirs(merge_save_path)
    sampled_save_path = os.path.join(base, "data", "sampled_data", '3DEPS')
    if not os.path.exists(sampled_save_path):
        os.makedirs(sampled_save_path)
    # 001 Batch separation of edges and centers of point clouds
    edge_separation_of_point_cloud(edge_save_path, core_save_path)
    # 002 Merge edge and non-edge parts by assigned number
    merge_edge_and_core(edge_save_path, core_save_path, merge_save_path)
    # 003 Composite point clouds proportionally and data augmentation
    downsampling_of_point_cloud(merge_save_path, sampled_save_path)
    # Sampling results are categorized and stored in respective folders by plant variety
    sort_plant(sampled_save_path)