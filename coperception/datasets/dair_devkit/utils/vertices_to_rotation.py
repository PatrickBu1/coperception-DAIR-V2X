from scipy.spatial.transform import Rotation as R
import numpy as np
import math


def vertices_to_rotation(point_matrix: np.ndarray):
    if point_matrix.shape != (8, 3):
        raise ValueError("Matrix should be 3d-locations of 8 points")

    four_pts = point_matrix[0:4]
    x = four_pts[:, 0]
    y = four_pts[:, 1]
    z = four_pts[:, 2]

    zero_ref = [i for i in point_matrix[0]]

    for i in range(4):
        x[i] -= zero_ref[0]
        y[i] -= zero_ref[1]
        z[i] -= zero_ref[2]

    z_angle = math.atan2(y[2], x[2])
    # y_angle = math.atan2(z[2], x[2])
    # x_angle = math.atan2(z[2], y[2])

    r = R.from_rotvec(np.array([0, 0, z_angle])).as_quat()
    return r.tolist()




