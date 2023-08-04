from omni.isaac.examples.base_sample import BaseSample
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage
from kafka import KafkaConsumer
import carb
import aiohttp
import asyncio
import numpy as np

from .server import request_data, fetch
from .utils.bounding_box import bbox_update, light_up, material_create
from .proprocess import BboxHandler
from .skeleton_visualize import SkeletonVisualizer
from .utils.util import map_scale_change
from .camera import camera_create, CAMERA_POSE_DICT
from .utils.kafka_consumer import kafka_pull_data


HOST = '203.250.148.120'
PORT = 20521
CONTAINER_NAME = "/Mobius/Daeyang_AI_Center/5F/Cam_1/Human/la"
ROOT_JOINT = 14
JOINT_NUM = 21
OBJECT = '0'
CAMERA_NUM = 1
# topic 이름도 입력으로 받아야함 개수만큼 -> 나중에 yaml 파일로 관리, 카메라 각도, 거리
# x, y 값만 depth값을 어느정도 줘야함

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self.post_id = []
        self.bbox_path = "/bbox_"
        self.bbox_process = BboxHandler()
        self.skeleton_visualizer = SkeletonVisualizer()
        self._topic = 'Cam_1'
        self._consumer = KafkaConsumer(
            bootstrap_servers=['203.250.148.120:20517'],
            auto_offset_reset='earliest',
            group_id='mygroup',
            enable_auto_commit=False
        )
        return

    def setup_scene(self):
        world = self.get_world()
        light_up()
        self.cnt = 0
        self.mtl_prim = material_create(OBJECT)
        # Camera 생성
        self.camera_list = camera_create(CAMERA_NUM)
        
        map_path = '/data/sejong/5f/5f_0919.usd'
        map_prim_path = "/World/DaeyangAICenter/Floor_5F"
        if map_path is None:
            # Use carb to log warnings, errors and infos in your application (shown on terminal)
            carb.log_error("Could not find Map file")
        # prim_path에 /앞에 숫자 있으면 안됨
        add_reference_to_stage(usd_path=map_path,  prim_path=map_prim_path)
        map_scale_change(map_prim_path)
        # world.scene.add_default_ground_plane()
        
        return

    async def _on_start_party_event_async(self):
        world = self.get_world()
        world.add_physics_callback("sim_step", self._on_start_party_physics_step)
        await world.play_async()
        return

    def _on_start_party_physics_step(self, step_size):
        # Mobius DB에 이미 저장되어 있는 데이터를 가져와서, 겹침
        point_set = []
        line_point_1 = []
        line_point_2 = []
        id = []
        root_pt = []
        root = []
        try:
            # asyncio.run(self._on_load_async())
            ### 해야할거 데이터 여러개 받아와서 카메라마다 방향, 위치 설정해주고 업데이트
            
            # for i in range(len(self.camera_list)):
            #     self.camera_list[0]
            
            
            # request_data(HOST, PORT, CONTAINER_NAME)
            
            # Request data from Mobius DB 
            # pos_data = request_data(HOST, PORT, CONTAINER_NAME)
            pos_data = kafka_pull_data(self._topic, self._consumer)
            # Kafka로부터 데이터를 가져옴 (Cam 1 ~ 6까지 데이터 가져오기)
            LoD = pos_data[0]["LoD"]

            # # 데이터에 id별로 list에 check 
            for idx in range(len(pos_data)):
                id.append(pos_data[idx]["id"])
                
            # # id가 순서가 불규칙적으로 들어오므로 id 정렬 
            id = sorted(id)
            self.post_id = sorted(self.post_id)
            
            
            
            
            
            # LoD 1 -> BBox
            if LoD == 1:
                self.cnt = self.bbox_process.handle_new_bbox(id, self.post_id, self.cnt, self.mtl_prim, self.bbox_path)
                # Update post_id
                self.post_id = id
                self.skeleton_visualizer.clear()
                root_pt, _, _, _ = self.skeleton_visualizer.pt_process(pos_data, root_pt, point_set, line_point_1, line_point_2)
                
                root = self.camera_list[0].camera_orient_change(root_pt, np.pi)
                root = self.camera_list[0].camera_trans_change(root, CAMERA_POSE_DICT['camera_1'][0]['translation'])
                
                for i in range(len(pos_data)):
                    bbox_update(root[i], id[i], self.bbox_path)
                    
            # LoD 2 -> BBox, Skeleton
            elif LoD == 2:
                self.cnt = self.bbox_process.handle_new_bbox(id, self.post_id, self.cnt, self.mtl_prim, self.bbox_path)
                # Update post_id
                
                self.post_id = id
                self.skeleton_visualizer.clear()
                root_pt, point_set, line_point_1, line_point_2 = self.skeleton_visualizer.pt_process(pos_data, root_pt, point_set, line_point_1, line_point_2)
                # BBox3D Translation update, 나중에 카메라 여러개로 바꿔야함
                # for i in range(len(CAMERA_NUM)):
                print(self.camera_list[0])
                # root_bbox, skeleton마다 카메라 위치 transform
                print('제발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발씨발')
                root_pt, point_set, line_point_1, line_point_2 = self.camera_list[0].camera_process(0, root_pt, point_set, line_point_1, line_point_2, 2)
                
                for i in range(len(pos_data)):
                    bbox_update(root_pt[i], id[i], self.bbox_path)
                self.skeleton_visualizer.draw_skeleton(point_set, line_point_1, line_point_2)
                print('------------------------------------------------')
            else:
                pass
            
            
        except Exception as e:
            print(e)
        return
    
    async def setup_post_reset(self):
        self.cnt = 0
        return