from .utils.bounding_box import create_3d_bbox
from omni.isaac.core.utils.prims import delete_prim
import numpy as np

ROOT_JOINT = 14

class BboxHandler:
    def __init__(self):
        pass

    def handle_new_bbox(self, id, post_id, cnt, mtl_prim, bbox_path):
        # id 개수가 전보다 많아진경우 -> 이전 id 데이터 초기화하고 새로 생성
        print(id)
        print(post_id)
        print(cnt)
        
        
        if len(id) > cnt:
            for idx in post_id:
                if idx in id:
                    continue
                else:
                    delete_prim(bbox_path + str(idx))
            cnt = len(id)
            
            # 이전데이터에서 추가 된 bbox 생성
            for idx in id:
                if idx in post_id:
                    continue
                else:
                    create_3d_bbox(idx, mtl_prim, bbox_path)

        # id 개수가 전보다 작아진 경우 -> id 새로운 데이터와 전에 데이터를 비교해서 없어지거나 새롭게 생긴 id 삭제 or 새롭게 생긴 bbox 생성
        elif len(id) < cnt:
            # 어떤 id가 없어졌는지 확인
            for idx in post_id:
                if idx in id:
                    continue
                else:
                    delete_prim(bbox_path + str(idx))
            
            # 새롭게 생긴 id bbox 생성 로직
            for idx in id:
                if idx in post_id:
                    continue
                else:
                    create_3d_bbox(idx, mtl_prim, bbox_path)
            cnt = len(id)
            

        # id 개수는 같은경우 
        # 1. id가 다른경우
        # 2. 그대로인 경우
        else:
            if id == post_id:
                pass
            else:
                for idx in post_id:
                    if idx in id:
                        continue
                    else:
                        delete_prim(bbox_path + str(idx))
                # 새롭게 생긴 id bbox 생성 로직
                for idx in id:
                    if idx in post_id:
                        continue
                    else:
                        create_3d_bbox(idx, mtl_prim, bbox_path)
        
        return cnt