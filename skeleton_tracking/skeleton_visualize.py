# from omni.isaac.debug_draw import _debug_draw
# from .utils.util import coordinate_process
# from .skeleton import EDGE
# import numpy as np
# ROOT_JOINT = 14

# class SkeletonVisualizer:
#     def __init__(self) -> None:
#         self._debug_draw = _debug_draw.acquire_debug_draw_interface()
        
#     def clear(self):
#         # Initialize pose, line
#         self._debug_draw.clear_points()
#         self._debug_draw.clear_lines()
        
#     def pt_process(self, pos_data, root_pt, point_set, line_point_1, line_point_2):
#         for elem in pos_data:
#             #한 개에 대해서 진행한다 생각
#             pos_ = np.array(elem["pose3d"])
#             pos_ = coordinate_process(pos_)
#             root_pt.append(pos_[ROOT_JOINT])
            
#             # Z 축에 값 + 1.5 해야함
#             pos = pos_.tolist()
#             # pos = list(map(tuple, pos))
#             point_set.extend(pos)
            
            
#             # j번째랑 j-1번째 연결하기 위한 points set을 구분 
#             for k in EDGE:
#                 line_point_1.append(pos[k[0]])
#                 line_point_2.append(pos[k[1]])
        
#         return root_pt, point_set, line_point_1, line_point_2
            
#     def draw_skeleton(self, point_set, line_point_1, line_point_2):
#         # Human point, line drawing
#         self._debug_draw.draw_points(point_set, [(0.75, 0.75, 1, 1)]*len(point_set), [10]*len(point_set))
#         self._debug_draw.draw_lines(line_point_1, line_point_2, [(0.75, 0.75, 1, 1)]*len(line_point_1), [2]*len(line_point_1))
    



from omni.isaac.debug_draw import _debug_draw
from .utils.util import coordinate_process
from .skeleton import EDGE
import numpy as np
ROOT_JOINT = 14

class SkeletonVisualizer:
    def __init__(self) -> None:
        self._debug_draw = _debug_draw.acquire_debug_draw_interface()
        
    def clear(self):
        # Initialize pose, line
        self._debug_draw.clear_points()
        self._debug_draw.clear_lines()
        
    def pt_process(self, pos_data, root_pt, point_set, line_point_1, line_point_2):
        for elem in pos_data:
            #한 개에 대해서 진행한다 생각
            pos_ = np.array(elem["pose3d"])
            pos_ = coordinate_process(pos_)
            root_pt.append(pos_[ROOT_JOINT])
            
            # Z 축에 값 + 1.5 해야함
            pos = pos_.tolist()
            # pos = list(map(tuple, pos))
            point_set.extend(pos)
            
            
            # j번째랑 j-1번째 연결하기 위한 points set을 구분 
            for k in EDGE:
                line_point_1.append(pos[k[0]])
                line_point_2.append(pos[k[1]])
        
        return root_pt, point_set, line_point_1, line_point_2
            
    def draw_skeleton(self, point_set, line_point_1, line_point_2):
        # Human point, line drawing
        self._debug_draw.draw_points(point_set, [(0.75, 0.75, 1, 1)]*len(point_set), [10]*len(point_set))
        self._debug_draw.draw_lines(line_point_1, line_point_2, [(0.75, 0.75, 1, 1)]*len(line_point_1), [2]*len(line_point_1))
    



