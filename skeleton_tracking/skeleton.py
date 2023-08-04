import copy
import os

import numpy as np
from carb.tokens import get_tokens_interface
from pxr import UsdSkel, Vt

# DEFAULT_SKEL_ROOT = "/World/char_poseEstimation_rig"
# DEFAULT_SKELETON = "/World/char_poseEstimation_rig/c_skeleton_grp/Root"

DEFAULT_SKEL_ROOT = "/World/SkelRoot0"
DEFAULT_SKELETON = "/World/SkelRoot0/Skeleton0/root"
EXT_ROOT = "/home/donghoon/.local/share/ov/pkg/isaac_sim-2022.2.1/exts/omni.isaac.examples/omni/isaac/examples/hello_world/Smplx2FBX/ExportShape"
TEMPLATE_SCENE_PATH = os.path.normpath(os.path.join(EXT_ROOT, "ExportShape.usd"))


class PoseTrackerSkeleton:
    def __init__(self, topology):
        self._topology = topology.copy()
        self._ref_pose = None
        self._rest_translations = None
        self._bind_translations = None
        self._joint_tokens = []

        for node in self._topology["nodes"]:
            path = node
            node_idx = self._topology["nodes"].index(node)
            while True:
                next_node = self._topology["parents"][node_idx]
                if next_node is "":
                    break
                path = next_node + "/" + path
                node_idx = self._topology["nodes"].index(next_node)
            self._joint_tokens.append(path)
        usd_topo = UsdSkel.Topology(self._joint_tokens)
        valid, whyNot = usd_topo.Validate()
        if not valid:
            raise ValueError("Invalid topology: {}".format(whyNot))

    def set_ref_pose(self, ref_pose):
        self._ref_pose = ref_pose.copy()
        self._rest_translations = []
        self._bind_translations = []
        
        for joint_full_name in self._joint_tokens:
            last_node = joint_full_name.split("/")[-1]
            last_node_idx = self._topology["nodes"].index(last_node)
            prev_node = self._topology["parents"][last_node_idx]
            if prev_node is "":
                rest_trans = self._ref_pose[last_node_idx]
            else:
                prev_node_idx = self._topology["nodes"].index(prev_node)
                rest_trans = self._ref_pose[last_node_idx] - self._ref_pose[prev_node_idx]
            bind_trans = self._ref_pose[last_node_idx]
            
            # point to point 차이 -> translate값으로 들어감
            self._rest_translations.append(rest_trans)
            self._bind_translations.append(bind_trans)
        # print(self._bind_translations)
            
    def get_rest_translations(self):
        return self._rest_translations

    def create_character(self, stage, idx):
        root_path = "/World/SkelRoot"
        def translation2transform(vec):
            t = np.eye(4)
            t[:-1, -1] = vec
            return t.T

        root_t = copy.deepcopy(self._rest_translations[0])
        root_t[0] = 0.0
        root_t[1] = 0.0
        root_t[2] = 0.0

        rest_translations = [root_t] + self._rest_translations
        bind_translations = [root_t] + self._bind_translations
        rest_transforms = Vt.Matrix4dArray.FromNumpy(
            np.array([translation2transform(x) for x in rest_translations])
        )
        bind_transforms = Vt.Matrix4dArray.FromNumpy(
            np.array([translation2transform(x) for x in bind_translations])
        )

        skel_root = UsdSkel.Root.Define(stage, root_path + str(idx))

        skel = UsdSkel.Skeleton.Define(stage, root_path + str(idx) + "/Skeleton{}".format(idx))
        joint_tokens = ["root"] + ["root/" + token for token in self._joint_tokens]

        # Skelton root이후 joint 생성
        skel.GetJointsAttr().Set(joint_tokens)
        # RestTransformsAttr: rest pose translation -> Local coordinate  
        skel.GetRestTransformsAttr().Set(rest_transforms)
        # BindTransformsAttr: bind pose translation -> Global coordinate
        skel.GetBindTransformsAttr().Set(bind_transforms)

        anim = UsdSkel.Animation.Define(stage, root_path + "/Skeleton/Anim")
        anim.GetJointsAttr().Set(joint_tokens)

        # SkelRoot/Skeleton에 Skeletal Animation 속성 부여
        binding = UsdSkel.BindingAPI.Apply(skel.GetPrim())
        # print(binding)
        # 위의 경로에 Animation Source binding
        binding.CreateAnimationSourceRel().SetTargets([anim.GetPrim().GetPath()])
        binding = UsdSkel.BindingAPI.Apply(skel_root.GetPrim())
        binding.CreateSkeletonRel().SetTargets([skel.GetPrim().GetPath()])


original_joints_name = ('Head_top', 'Thorax', 'R_Shoulder', 'R_Elbow', 'R_Wrist', 'L_Shoulder',
               'L_Elbow', 'L_Wrist', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee',
               'L_Ankle', 'Pelvis', 'Spine', 'Head', 'R_Hand', 'L_Hand', 'R_Toe', 'L_Toe')


BODY_INDEX = { "Pelvis": 0, "L_Hip": 1, "R_Hip": 2, "Spine": 3, "L_Knee": 4,
                "R_Knee": 5, "Thorax": 6, "L_Ankle": 7, "R_Ankle": 8, "L_Toe": 9,
                "R_Toe": 10, "Head": 11, "Head_top": 12, "L_Shoulder": 13, "R_Shoulder": 14,
                "L_Elbow": 15, "R_Elbow": 16, "L_Wrist": 17, "R_Wrist": 18, "L_Hand": 19, "R_Hand": 20 }

BODY_TOPOLOGY = {
        "nodes" : [
                "Pelvis",
                "L_Hip",
                "R_Hip",
                "Spine",
                "L_Knee",
                "R_Knee",
                "Thorax",
                "L_Ankle",
                "R_Ankle",
                "L_Toe",
                "R_Toe", # 11
                "Head",
                "Head_top",
                "L_Shoulder",
                "R_Shoulder",
                "L_Elbow",
                "R_Elbow",
                "L_Wrist",
                "R_Wrist",
                "L_Hand",
                "R_Hand",
        ],
        "parents": [
                "",
                "Pelvis",
                "Pelvis",
                "Pelvis",
                "L_Hip",
                "R_Hip",
                "Spine",
                "L_Knee",
                "R_Knee",
                "L_Ankle",
                "R_Ankle", # 11
                "Thorax",
                "Head",
                "Thorax",
                "Thorax",
                "L_Shoulder",
                "R_Shoulder",
                "L_Elbow",
                "R_Elbow",
                "L_Wrist",
                "R_Wrist",
        ]
        
}


class FROM_BODY_PARTS:
    Pelvis = 0
    L_Hip = 1
    R_Hip = 2
    Spine = 3
    L_Knee = 4
    R_Knee = 5
    Thorax = 6
    L_Ankle = 7
    R_Ankle = 8
    L_Toe = 9
    R_Toe = 10
    Head = 11
    Head_top = 12
    L_Shoulder = 13
    R_Shoulder = 14
    L_Elbow = 15
    R_Elbow = 16
    L_Wrist = 17
    R_Wrist = 18
    L_Hand = 19
    R_Hand = 20
    
    

class TO_SKEL_JOINTS:
    Root = 0
    Pelvis = 1
    Spine1 = 2
    Spine2 = 3
    Chest = 4
    Neck1 = 5
    Neck2 = 6
    Head = 7
    HeadEnd = 8
    Jaw = 9
    L_Eye = 10
    R_Eye = 11
    Nose = 12
    L_Ear = 13
    R_Ear = 14
    L_Clavicle = 15
    L_UpArm = 16
    L_LoArm = 17
    L_Wrist = 18
    L_ThumbFinger1 = 19
    L_ThumbFinger2 = 20
    L_ThumbFinger3 = 21
    L_ThumbFingerEnd = 22
    L_IndexFinger1 = 23
    L_IndexFinger2 = 24
    L_IndexFinger3 = 25
    L_IndexFinger4 = 26
    L_IndexFingerEnd = 27
    L_MiddleFinger1 = 28
    L_MiddleFinger2 = 29
    L_MiddleFinger3 = 30
    L_MiddleFinger4 = 31
    L_MiddleFingerEnd = 32
    L_RingFinger1 = 33
    L_RingFinger2 = 34
    L_RingFinger3 = 35
    L_RingFinger4 = 36
    L_RingFingerEnd = 37
    L_PinkyFinger1 = 38
    L_PinkyFinger2 = 39
    L_PinkyFinger3 = 40
    L_PinkyFinger4 = 41
    L_PinkyFingerEnd = 42
    L_LoArmTwist1 = 43
    L_UpArmTwist1 = 44
    R_Clavicle = 45
    R_UpArm = 46
    R_LoArm = 47
    R_Wrist = 48
    R_ThumbFinger1 = 49
    R_ThumbFinger2 = 50
    R_ThumbFinger3 = 51
    R_ThumbFingerEnd = 52
    R_IndexFinger1 = 53
    R_IndexFinger2 = 54
    R_IndexFinger3 = 55
    R_IndexFinger4 = 56
    R_IndexFingerEnd = 57
    R_MiddleFinger1 = 58
    R_MiddleFinger2 = 59
    R_MiddleFinger3 = 60
    R_MiddleFinger4 = 61
    R_MiddleFingerEnd = 62
    R_RingFinger1 = 63
    R_RingFinger2 = 64
    R_RingFinger3 = 65
    R_RingFinger4 = 66
    R_RingFingerEnd = 67
    R_PinkyFinger1 = 68
    R_PinkyFinger2 = 69
    R_PinkyFinger3 = 70
    R_PinkyFinger4 = 71
    R_PinkyFingerEnd = 72
    R_LoArmTwist1 = 73
    R_UpArmTwist1 = 74
    L_UpLeg = 75
    L_LoLeg = 76
    L_Ankle = 77
    L_Ball = 78
    L_Toe = 79
    L_BigToe = 80
    L_PinkyToe = 81
    L_Heel = 82
    L_LoLegTwist1 = 83
    L_UpLegTwist1 = 84
    R_UpLeg = 85
    R_LoLeg = 86
    R_Ankle = 87
    R_Ball = 88
    R_Toe = 89
    R_BigToe = 90
    R_PinkyToe = 91
    R_Heel = 92
    R_LoLegTwist1 = 93
    R_UpLegTwist1 = 94


# joints_name = ('Head_top', 'Thorax', 'R_Shoulder', 'R_Elbow', 'R_Wrist', 'L_Shoulder',
#                'L_Elbow', 'L_Wrist', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee',
#                'L_Ankle', 'Pelvis', 'Spine', 'Head', 'R_Hand', 'L_Hand', 'R_Toe', 'L_Toe')

BODY_INDEX = { "Head_top": 0, "Thorax": 1, "R_Shoulder": 2, "R_Elbow": 3, "R_Wrist": 4,
                "L_Shoulder": 5, "L_Elbow": 6, "L_Wrist": 7, "R_Hip": 8, "R_Knee": 9,
                "R_Ankle": 10, "L_Hip": 11, "L_Knee": 12, "L_Ankle": 13, "Pelvis": 14,
                "Spine": 15, "Head": 16, "R_Hand": 17, "L_Hand": 18, "R_Toe": 19, "L_Toe": 20 }

POSE_PAIRS = [ ["Head_top", "Head"], ["Head", "Thorax"], ["Thorax", "Spine"],
                ["Spine", "Pelvis"], ["Pelvis", "R_Hip"], ["Pelvis", "L_Hip"],
                ["R_Hip", "R_Knee"], ["R_Knee", "R_Ankle"], ["R_Ankle", "R_Toe"], ["L_Hip", "L_Knee"],
                ["L_Knee", "L_Ankle"], ["L_Ankle", "L_Toe"], ["Thorax", "R_Shoulder"], ["R_Shoulder", "R_Elbow"],
                ["R_Elbow", "R_Wrist"], ["R_Wrist", "R_Hand"], ["Thorax", "L_Shoulder"], ["L_Shoulder", "L_Elbow"],
                ["L_Elbow", "L_Wrist"], ["L_Wrist", "L_Hand"]]


# flip_pairs = ( (2, 5), (3, 6), (4, 7), (8, 11), (9, 12), (10, 13), (17, 18), (19, 20) )
EDGE = [[0, 16], [16, 1], [1, 15], [15, 14], [14, 8], [14, 11], [8, 9], [9, 10], [10, 19], 
        [11, 12], [12, 13], [13, 20], [1, 2], [2, 3], [3, 4], [4, 17], [1, 5], [5, 6], [6, 7], [7, 18]]

# BODY_TOPOLOGY = {
#         "nodes" : [
#                 "Head_top",
#                 "Thorax",
#                 "R_Shoulder",
#                 "R_Elbow",
#                 "R_Wrist",
#                 "L_Shoulder",
#                 "L_Elbow",
#                 "L_Wrist",
#                 "R_Hip",
#                 "R_Knee",
#                 "R_Ankle",
#                 "L_Hip",
#                 "L_Knee",
#                 "L_Ankle",
#                 "Pelvis",
#                 "Spine",
#                 "Head",
#                 "R_Hand",
#                 "L_Hand",
#                 "R_Toe",
#                 "L_Toe",
#         ],
#         "parents": [
#                 "",
#                 "Head",
#                 "Thorax",
#                 "R_Shoulder",
#                 "R_Elbow",
#                 "Thorax",
#                 "L_Shoulder",
#                 "L_Elbow",
#                 "Pelvis",
#                 "R_Hip",
#                 "R_Knee",
#                 "Pelvis",
#                 "L_Hip",
#                 "L_Knee",
#                 "Spine",
#                 "Thorax",
#                 "Head_top",
#                 "R_Wrist",
#                 "L_Wrist",
#                 "R_Ankle",
#                 "L_Ankle",
#         ]
        
# }


# class BODY_PARTS:
#     Head_top = 0
#     Thorax = 1
#     R_Shoulder = 2
#     R_Elbow = 3
#     R_Wrist = 4
#     L_Shoulder = 5
#     L_Elbow = 6
#     L_Wrist = 7
#     R_Hip = 8
#     R_Knee = 9
#     R_Ankle = 10
#     L_Hip = 11
#     L_Knee = 12
#     L_Ankle = 13
#     Pelvis = 14
#     Spine = 15
#     Head = 16
#     R_Hand = 17
#     L_Hand = 18
#     R_Toe = 19
#     L_Toe = 20
    
    

