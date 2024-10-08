# TrackPlant3D: 3D organ growth tracking framework for organ-level dynamic phenotyping

## Prerequisites
- Python == 3.7
- matplotlib == 3.3.4
- numpy == 1.19.5
- scipy == 1.5.4

## Introduction
The extraction of dynamic plant phenotypes is highly important for understanding the process of plant phenotype formation and formulating growth management plans. Although rapid progress has been made in the analysis of the efficiency and throughput of static phenotypes, dynamic growth tracking methods are still a key bottleneck for dynamic phenotyping. The major challenges related to organ growth tracking include the nonrigid deformation of organ morphology during growth, the high frequency of growth events, and a lack of spatiotemporal datasets. 

Inspired by the phenomenon in which a human naturally compares two similar three-dimensional objects by overlapping and aligning them, this study proposes an automatic organ growth tracking framework—TrackPlant3D—for time-series crop point clouds. The unsupervised framework takes crop point clouds at multiple growth stages with organ instance labels as input and produces point clouds with consistent organ labels as organ-level growth tracking outputs. Compared with the other two state-of-the-art organ tracking methods, TrackPlant3D has better tracking performance and greater adaptability across species. 

In an experiment involving maize species, the long-term and short-term tracking accuracies of TrackPlant3D both reached 100%. For sorghum, tobacco and tomato crops, the long-term tracking accuracies were 81.25%, 64.13% and 86.75%, respectively, and the short-term tracking accuracies were all greater than 85.00%, demonstrating satisfactory tracking performance. Moreover, TrackPlant3D is also robust against frequent organ growth events and adaptable to different types of segmentation inputs as well as to inputs involving inclination and rotation disturbances. We also demonstrated that the TrackPlant3D framework has the potential for incorporation into a fully automatic dynamic phenotyping pipeline that integrates organ segmentation, organ tracking, and dynamic monitoring of phenotypic traits such as individual leaf length and leaf area. This study may contribute to the development of dynamic phenotyping, digital agriculture, and the factory production of plants.


***<p align="center">Overall TrackPlant3D framework for tracking organ growth in time-series plant point clouds.<br>The framework includes three main steps—Step 1, point cloud processing; Step 2, estimating organ correspondences; and Step 3, growth tracking***<br>
<img src="img/TrackPlant3D.jpg" width="100%" height="50%"><br><br>

## Quick Start
The project contains five folders.<br>
Folder __[data]__ contains four subfolders corresponding to the original data, sampled data, registration results and tracking results respectively. <br>
Folder __[downsampling]__ contains code for downsampling point clouds.<br>
Folder __[registration]__ contains code for registering point clouds.<br>
Folder __[tracking]__ contains code for tracking plant organs.<br>
Folder __[evaluation]__ contains code for calculating the accuracy of plant organ tracking results.<br>

### Downsampling  
Downsampling the point cloud can reduce the computational burden and the time cost for registration.In downsampling process, 3D Edge‑Preserving Sampling (3DEPS) is used to downsample the point cloud.
- File `001Batch separation of edges and centers of point clouds(c++).cpp` is used to separate original point clouds into point clouds containing only edge points and point clouds containing only non-edge points (in batches), respectively.
- File `002Merge edge and non-edge parts by assigned number.py` uses FPS to randomly sample 4096 points from the edge part and sample 4096 points from the non-edge part, and combine the two parts into a new point cloud with 4096+4096 points.
- File `003Composite point clouds proportionally and data augmentation.py` uses FPS to sample 256*(ratio) points from the edge part and to sample 256*(1-ratio) points from the non-edge part, then merges the two parts into a new single point cloud with 256 points. Finally, normalize the downsampled point cloud. Data augmentation is not required in our experiments.

### Registration 
Non-rigid registration method coherent point drift(CPD) is used to improve the relative position of point clouds at adjacent moments.<br> 
- The input of registration is downsampling results saved in folder `./data/sampled_data`. 
- The output of registration will be saved in folder `./data/registration_result`
- File `fish_deformable_3D_lowrank_my.py` take point cloud at time ***t-1*** and point cloud at time ***t*** as input and return the transformed point cloud at time ***t***.

### Tracking 
Organ tracking algorithm obtains organ correspondences through bipartite matching. <br>
- The input of tracking is registration results at time ***t*** in folder `./data/registration_result` and the downsampled point cloud at time ***t-1*** in folder `./data/sampled_data`. 
- The output are point clouds whose labels are upsampled to propagate to the original point clouds will be saved in `./data/tracking_result`.
- File `organ_matching.py` estimates the organ correspondences between point cloud at time ***t-1*** and point cloud at time ***t***.
- Folder `./tracking/cost` stores the extended cost matrix of each tracking.
- Folder `./tracking/col` stores the organ correspondences of each tracking.

### Evaluation
- The input is GTs in folder `./data/original_data/gt` and tracking results in folder `./data/tracking_result`.
- Files `match.py` and `evalutaion.py` should be executed in turn to obtain quantitative metrics.
- The output will be stored in the current folder.
