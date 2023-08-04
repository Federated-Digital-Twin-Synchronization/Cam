import omni
from omni.isaac.core.utils.prims import delete_prim
import numpy as np
from .bounding_box import create_3d_bbox

OBJECT = '0'

def order_change_pose(pos):
    tmp = pos.copy()
    pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6], pos[7], pos[8], pos[9], pos[10], pos[11], pos[12], pos[13], pos[14], pos[15], pos[16], pos[17], pos[18], pos[19], pos[20] = tmp[14], tmp[11], tmp[8], tmp[15], tmp[12], tmp[9], tmp[1], tmp[13], tmp[10], tmp[20], tmp[19], tmp[16], tmp[0], tmp[5], tmp[2], tmp[6], tmp[3], tmp[7], tmp[4], tmp[18], tmp[17]
    return pos

# camera -> xyz 좌표 변환 
# def change_coordinate(pos):
#     pos /= np.linalg.norm(pos)
#     pos *= 15
#     # print(pos)
#     for i in range(len(pos)):
#         temp = pos[i][0]
#         pos[i][0] = pos[i][2]
#         pos[i][2] = -1*pos[i][1]
#         pos[i][1] = temp
#     # pos = order_change_pose(pos)
#     return pos

# camera coordinate (w : x(left), h : y(down) depth : z) -> xyz 좌표 변환 
def change_coordinate(pos):
    pos /= np.linalg.norm(pos)
    pos *= 8
    for i in range(len(pos)):
        temp = pos[i][1]
        pos[i][1] = pos[i][2]
        pos[i][2] = -1*temp
    return pos


def coordinate_process(pos):
    pos = change_coordinate(pos)
    pos = correction_coordinate(pos)
    return pos


def correction_coordinate(pos):
    for _ in range(len(pos)):
        pos_ = np.array(pos)
        pos_[:, 2] += 1.1
    return pos_

            
def map_scale_change(path, scale=(0.01, 0.01, 0.01)):
    omni.kit.commands.execute(
        "IsaacSimScalePrim",
        prim_path=path,
        scale=scale
    )

