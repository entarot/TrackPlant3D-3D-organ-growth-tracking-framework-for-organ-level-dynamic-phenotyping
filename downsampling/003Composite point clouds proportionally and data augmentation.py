# -*- coding: utf-8 -*-

import numpy as np
import math
import time
import sys
import os
from utils import *
# import numba
# from numba import jit


def get_filelist(path):
    Filelist = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            Filelist.append(os.path.join(home, filename))
    return Filelist

##Class: FarthestSampler
class FarthestSampler:
    def __init__(self):
        pass
    def _calc_distances(self, p0, points):
        return ((p0 - points) ** 2).sum(axis=1)  #Returns the sum of squared Euclidean distances between the set of sample points and other points
    def _call__(self, pts, k):  #PTS is the input point cloud,  K is the number of downsampling
        farthest_pts = np.zeros((k, 4), dtype=np.float32) #  The first three columns are coordinates xyz, and the fourth column is labels
        farthest_pts[0] = pts[np.random.randint(len(pts))]
        distances = self._calc_distances(farthest_pts[0,:3], pts[:,:3])
        for i in range(1, k):
            farthest_pts[i] = pts[np.argmax(distances)]
            distances = np.minimum( distances, self._calc_distances(farthest_pts[i,:3], pts[:,:3]))
        return farthest_pts

'''
    input:  Merged points in the format of the TXT by xyzLabel
	output: 3DEPS TXT dataset in the form of XYZLabel
'''


if __name__ == '__main__':
    path = r'D:\Zealot\论文\2024-7-29\github模板\data\sampled_data\3Deps\merge'  #your merged points directory path
    saved_path = r'D:\Zealot\论文\2024-7-29\github模板\data\sampled_data\maize'  #save path of 3DEPS points
    files = os.listdir(path)
    for i in range(len(files)):
        print(files[i])
        points = np.loadtxt(os.path.join(path,files[i]))

        pcd_array=np.array(points)
        print("pcd_array.shape:", pcd_array.shape)
        sample_count = 256  # Fixed number of points after FPS downsampling
        ratio = 0.5 # proportionality ratio 设置为0.5
        CoreNum=4096 # Number of center points in merged data

        # Perform FPS Downsampling for center point set and edge point set respectively
        FPS = FarthestSampler()  #
        center_points = FPS._call__(pcd_array[0:CoreNum, 0:4],sample_count - int(sample_count * ratio))
        edg_points = FPS._call__(pcd_array[CoreNum:, 0:4], int(sample_count * ratio))
        sample_points = np.concatenate((center_points, edg_points), axis=0)  # joint into a new point cloud
        norm_point = pointnet_norm(sample_points[:,:3])
        final_points = np.hstack((norm_point, sample_points[:,-1].reshape(-1,1)))
        #Obtain the file name under the path and remove the suffix
        np.savetxt(os.path.join(saved_path,files[i]), final_points, fmt='%.6f')  # Save 3DEPS TXT in the form of XYZLabel
