import numpy as np

def camera_create(num):
    cameras = [Camera(id=i+1) for i in range(num)]
    return cameras

class Camera:
    def __init__(self, id) -> None:
        self.id = id
        self.pos_data = None
        self.topic = 'Cam_' + str(self.id)
        
    def camera_orient_change(self, point, angle):
        # angle = np.pi  # 90도를 라디안으로 변환
        pos = []
        for i in range(len(point)):
            pt = point[i]
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle),  np.cos(angle)]
            ])

            reshaped_point = pt[:2]
            rotated_vector = np.dot(reshaped_point, rotation_matrix)
            pos.append(np.append(rotated_vector, pt[2]))  # Fixed
        return pos

    def camera_trans_change(self, pos, cam_pos):
        pos = np.array(pos) + cam_pos
        pos = pos.tolist()
        return pos
    
        
    def camera_process(self, cam_id, root_pt, point_set=None, line_point_1=None, line_point_2=None, LoD=0):
        
        cam_id += 1
        cam_path = 'camera_' + str(cam_id)
        
        if LoD == 1:
            root = self.camera_orient_change(root_pt, CAMERA_POSE_DICT[cam_path][0]['orientation'])
            root = self.camera_trans_change(root, CAMERA_POSE_DICT[cam_path][0]['translation'])
            return root

        elif LoD == 2:
            root = self.camera_orient_change(root_pt, CAMERA_POSE_DICT[cam_path][0]['orientation'])
            root = self.camera_trans_change(root, CAMERA_POSE_DICT[cam_path][0]['translation'])
            
            point_set = self.camera_orient_change(point_set, CAMERA_POSE_DICT[cam_path][0]['orientation'])
            line_point_1 = self.camera_orient_change(line_point_1, CAMERA_POSE_DICT[cam_path][0]['orientation'])
            line_point_2 = self.camera_orient_change(line_point_2, CAMERA_POSE_DICT[cam_path][0]['orientation'])

            point_set = self.camera_trans_change(point_set, CAMERA_POSE_DICT[cam_path][0]['translation'])
            line_point_1 = self.camera_trans_change(line_point_1, CAMERA_POSE_DICT[cam_path][0]['translation'])
            line_point_2 = self.camera_trans_change(line_point_2, CAMERA_POSE_DICT[cam_path][0]['translation'])
            
            return root, point_set, line_point_1, line_point_2
    

CAMERA_POSE_DICT = {
    'camera_1': [{
        'orientation' : np.pi,
        'translation' : [1.0, 1.0, 0.0]
    }],
    'camera_2': [{
        'orientation' : np.pi/2,
        'translation' : [1.0, 2.0, 0.0]
    }],
    'camera_3': [{
        'orientation' : np.pi*2,
        'translation' : [1.0, 3.0, 0.0]
    }],
    'camera_4': [{
        'orientation' : np.pi,
        'translation' : [-12.0, 1.0, 0.0]
    }],
    'camera_5': [{
        'orientation' : np.pi/2,
        'translation' : [-12.0, 2.0, 0.0]
    }],
    'camera_6': [{
        'orientation' : np.pi*2,
        'translation' : [-12.0, 3.0, 0.0]
    }],
}