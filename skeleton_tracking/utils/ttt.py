from omni.isaac.core.objects import DynamicCuboid
from omni.isaac.core.materials import VisualMaterial
from omni.isaac.core.utils.nucleus import get_assets_root_path
from pxr import UsdShade, Sdf, UsdGeom, Gf
import numpy as np
import omni
import carb
import omni.kit.commands
from omni.isaac.core.materials.visual_material import VisualMaterial

def Bbox3D(object, translation):
    if object == '0':
        mtl_created_list = []
        # Create a new material using OmniGlass.mdl
        ## mdl_name에 경로 넣어주기
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary",
            mdl_name="omniverse://localhost/NVIDIA/Materials/2023_1/Base/Glass/Blue_Glass.mdl",
            mtl_name="Blue_Glass",
            mtl_created_list=mtl_created_list,
        )
        
        
    elif object == '1':
        mtl_created_list = []
        # Create a new material using OmniGlass.mdl
        ## mdl_name에 경로 넣어주기
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary",
            mdl_name="omniverse://localhost/NVIDIA/Materials/2023_1/Base/Glass/Green_Glass.mdl",
            mtl_name="Green_Glass",
            mtl_created_list=mtl_created_list,
        )
    
    # Get reference to created material
    stage = omni.usd.get_context().get_stage()
    mtl_prim = stage.GetPrimAtPath(mtl_created_list[0])
    # Create a prim to apply the material to
    result, path = omni.kit.commands.execute(
        "CreateMeshPrimCommand", 
        prim_type="Cube",
        prim_path="/Cube_1"
        )
    print(path)
    # Get the path to the prim
    cube_prim = stage.GetPrimAtPath(path)
    # Bind the material to the prim
    cube_mat_shade = UsdShade.Material(mtl_prim)
    xform = UsdGeom.Xformable(cube_prim)
    UsdShade.MaterialBindingAPI(cube_prim).Bind(cube_mat_shade, UsdShade.Tokens.strongerThanDescendants)
    UsdGeom.Xformable(cube_prim).AddTranslateOp().Set(translation)
    UsdGeom.Xformable(cube_prim).AddRotateXYZOp().Set((0., 0., 0.))
    UsdGeom.Xformable(cube_prim).AddScaleOp().Set((0.5, 0.5, 1.))
    return cube_prim


def bbox_update(trans):
    omni.kit.commands.execute(
        "IsaacSimTeleportPrim",
        prim_path="/Cube",
        translation=(trans[0],trans[1],trans[2]),
    )
    
    omni.kit.commands.execute(
        "IsaacSimScalePrim",
        prim_path="/Cube",
        scale=(0.5, 0.5, 1.)
    )

# pos_ = np.array([[175.6921844482422, -419.2813415527344, 1514.895263671875], [146.99423217773438, -249.10504150390625, 1609.5123291015625], [58.16099166870117, -255.555419921875, 1581.18603515625], [-10.29085922241211, -134.77291870117188, 1604.2891845703125], [21.112642288208008, -11.06359577178955, 1612.51904296875], [231.80897521972656, -240.8822021484375, 1608.992919921875], [242.84188842773438, -111.1834487915039, 1657.7913818359375], [191.0279541015625, -20.07088279724121, 1620.8529052734375], [43.5770149230957, 4.931811332702637, 1660.35986328125], [-11.841379165649414, 228.69517517089844, 1651.4462890625], [-86.73947143554688, 493.3585205078125, 1689.5263671875], [141.89691162109375, 19.305198669433594, 1675.2838134765625], [146.56300354003906, 244.21963500976562, 1669.224853515625], [147.0784454345703, 493.19110107421875, 1711.486572265625], [95.819580078125, 8.251457214355469, 1681.7349853515625], [121.47915649414062, -138.09205627441406, 1686.2308349609375], [156.9030303955078, -313.1472473144531, 1548.75390625], [20.295663833618164, 32.40049743652344, 1670.1922607421875], [179.55532836914062, 22.325096130371094, 1662.0126953125], [-105.57808685302734, 473.02838134765625, 1567.88623046875], [123.36953735351562, 473.5940246582031, 1613.0137939453125]])