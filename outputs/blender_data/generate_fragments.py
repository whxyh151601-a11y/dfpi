
import bpy
import json
import random
import math
import os

# ── 配置路径（修改为你自己的实际路径）────────────────────────────
DATA_DIR = r"C:\Users\Mordecai\Desktop\claude\backrooms_project\outputs\blender_data"

# ── 1. 读取数据 ───────────────────────────────────────────────────
with open(os.path.join(DATA_DIR, "cluster_centers.json")) as f:
    centers = json.load(f)

# ── 2. 清空场景 ───────────────────────────────────────────────────
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# ── 3. 碎片生成函数 ───────────────────────────────────────────────
def create_fragment(x, y, z, cluster_id, fragment_id):
    if cluster_id == 0:
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
        obj = bpy.context.active_object
        obj.scale = (random.uniform(1.5,3.0), random.uniform(1.5,3.0), random.uniform(0.05,0.2))
    elif cluster_id == 1:
        bpy.ops.mesh.primitive_cylinder_add(location=(x, y, z))
        obj = bpy.context.active_object
        obj.scale = (random.uniform(0.2,0.5), random.uniform(0.2,0.5), random.uniform(1.5,4.0))
    elif cluster_id == 2:
        bpy.ops.mesh.primitive_torus_add(location=(x, y, z),
            major_radius=random.uniform(0.5,1.2), minor_radius=random.uniform(0.1,0.3))
        obj = bpy.context.active_object
        obj.scale = (1, 1, random.uniform(0.3,0.8))
    elif cluster_id == 3:
        bpy.ops.mesh.primitive_cone_add(location=(x, y, z))
        obj = bpy.context.active_object
        obj.scale = (random.uniform(0.3,0.8), random.uniform(0.3,0.8), random.uniform(2.0,5.0))
    else:
        bpy.ops.mesh.primitive_plane_add(location=(x, y, z))
        obj = bpy.context.active_object
        obj.scale = (random.uniform(1.0,2.5), random.uniform(0.05,0.15), random.uniform(1.0,3.0))

    obj.rotation_euler = (
        random.uniform(-0.3, 0.3),
        random.uniform(-0.3, 0.3),
        random.uniform(0, math.pi * 2)
    )
    obj.name = f"Fragment_{cluster_id}_{fragment_id:03d}"
    return obj

# ── 4. 材质函数 ───────────────────────────────────────────────────
def create_material(cluster_id):
    colors = {
        0: (0.4, 0.6, 0.8, 1),
        1: (0.5, 0.3, 0.6, 1),
        2: (0.7, 0.5, 0.3, 1),
        3: (0.4, 0.2, 0.5, 1),
        4: (0.3, 0.5, 0.6, 1),
    }
    mat = bpy.data.materials.new(name=f"Mat_Cluster_{cluster_id}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = colors.get(cluster_id, (0.5,0.5,0.5,1))
    bsdf.inputs["Roughness"].default_value  = random.uniform(0.3, 0.8)
    bsdf.inputs["Metallic"].default_value   = random.uniform(0.0, 0.5)
    return mat

# ── 5. 生成25个碎片 ───────────────────────────────────────────────
print("生成建筑碎片...")
all_fragments = []
fragment_count = 0

for center in centers:
    cid = center["cluster_id"]
    cx, cy, cz = center["x"], center["y"], center["z"]
    mat = create_material(cid)
    for i in range(5):
        x = cx + random.uniform(-3, 3)
        y = cy + random.uniform(-3, 3)
        z = cz + random.uniform(0, 2)
        obj = create_fragment(x, y, z, cid, fragment_count)
        obj.data.materials.append(mat)
        all_fragments.append(obj)
        fragment_count += 1

print(f"共生成 {fragment_count} 个碎片")

# ── 6. 灯光 ──────────────────────────────────────────────────────
bpy.ops.object.light_add(type="SUN", location=(10, 10, 20))
bpy.context.active_object.data.energy = 2.0
bpy.ops.object.light_add(type="POINT", location=(0, 0, 10))
bpy.context.active_object.data.energy = 500
bpy.context.active_object.data.color  = (0.7, 0.85, 1.0)

# ── 7. 摄像机 ────────────────────────────────────────────────────
bpy.ops.object.camera_add(location=(15, -15, 10))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(55), 0, math.radians(45))
bpy.context.scene.camera = cam

# ── 8. 动画关键帧 ─────────────────────────────────────────────────
for obj in all_fragments:
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.rotation_euler.z += math.pi * 2
    obj.keyframe_insert(data_path="rotation_euler", frame=250)

bpy.context.scene.frame_end = 250
print("完成！按 Space 预览动画")
