
import bpy
import json
import random
import math
import os

# ── Configuration ─────────────────────────────────────────────
DATA_DIR = r"C:\Users\YourName\backrooms_project\outputs\blender_data"

with open(os.path.join(DATA_DIR, "cluster_centers_v2.json")) as f:
    centers = json.load(f)

# ── Clear scene ───────────────────────────────────────────────
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# ── Fragment generator ────────────────────────────────────────
def create_fragment(x, y, z, cluster_id, frag_id):
    """
    Cluster 0 = Liminal Architecture A → flat corridor slabs
    Cluster 1 = Pool Rooms            → curved pool-like forms
    Cluster 2 = Liminal Architecture B → tall brutalist pillars
    """
    if cluster_id == 0:
        # Flat horizontal slabs — corridor floors/ceilings
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
        obj = bpy.context.active_object
        obj.scale = (
            random.uniform(2.0, 5.0),
            random.uniform(2.0, 5.0),
            random.uniform(0.03, 0.12)
        )
    elif cluster_id == 1:
        # Curved pool forms — shallow dishes
        bpy.ops.mesh.primitive_cylinder_add(
            location=(x, y, z),
            vertices=32,
            radius=random.uniform(0.8, 2.0),
            depth=random.uniform(0.1, 0.4)
        )
        obj = bpy.context.active_object
        obj.scale = (1, 1, random.uniform(0.1, 0.3))
    else:
        # Tall brutalist pillars — vertical walls
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
        obj = bpy.context.active_object
        obj.scale = (
            random.uniform(0.1, 0.4),
            random.uniform(1.5, 4.0),
            random.uniform(2.0, 6.0)
        )

    obj.rotation_euler = (
        random.uniform(-0.15, 0.15),
        random.uniform(-0.15, 0.15),
        random.uniform(0, math.pi * 2)
    )
    obj.name = f"Fragment_{cluster_id}_{frag_id:03d}"
    return obj

# ── Material creator ──────────────────────────────────────────
def create_material(cluster_id):
    """
    Cluster 0 = warm concrete grey
    Cluster 1 = cold pool tile blue
    Cluster 2 = brutalist dark grey
    """
    palette = {
        0: (0.55, 0.52, 0.48, 1),   # warm concrete
        1: (0.35, 0.55, 0.65, 1),   # pool tile blue
        2: (0.28, 0.28, 0.30, 1),   # brutalist dark
    }
    mat = bpy.data.materials.new(name=f"Mat_{cluster_id}_{random.randint(0,999)}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf  = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs[0].default_value = palette.get(cluster_id, (0.5,0.5,0.5,1))
    bsdf.inputs[2].default_value = random.uniform(0.6, 0.95)   # roughness
    bsdf.inputs[1].default_value = random.uniform(0.0, 0.15)   # metallic
    return mat

# ── Generate 30 fragments (10 per cluster) ────────────────────
print("Generating architectural fragments...")
all_fragments = []
frag_count    = 0

for center in centers:
    cid = center["cluster_id"]
    cx, cy, cz = center["x"], center["y"], center["z"]
    mat = create_material(cid)

    for i in range(10):   # 10 per cluster = 30 total
        x = cx + random.uniform(-4, 4)
        y = cy + random.uniform(-4, 4)
        z = cz + random.uniform(0,  3)
        obj = create_fragment(x, y, z, cid, frag_count)

        # Add subdivision for organic surface
        mod          = obj.modifiers.new("Sub", "SUBSURF")
        mod.levels   = 1
        tex          = bpy.data.textures.new(f"T_{frag_count}", "MUSGRAVE")
        tex.noise_scale = random.uniform(0.3, 1.5)
        disp         = obj.modifiers.new("Disp", "DISPLACE")
        disp.texture = tex
        disp.strength = random.uniform(0.01, 0.08)

        obj.data.materials.append(mat)
        all_fragments.append(obj)
        frag_count += 1

print(f"Generated {frag_count} fragments")

# ── Lighting ──────────────────────────────────────────────────
# Main overhead fluorescent (liminal feel)
bpy.ops.object.light_add(type="AREA", location=(0, 0, 15))
main = bpy.context.active_object
main.data.energy = 1200
main.data.color  = (0.95, 0.97, 1.0)
main.data.size   = 10

# Cold blue fill (pool rooms)
bpy.ops.object.light_add(type="POINT", location=(-10, 0, 4))
fill1 = bpy.context.active_object
fill1.data.energy = 400
fill1.data.color  = (0.4, 0.6, 1.0)

# Warm amber accent (liminal warmth)
bpy.ops.object.light_add(type="POINT", location=(10, 8, 2))
fill2 = bpy.context.active_object
fill2.data.energy = 200
fill2.data.color  = (1.0, 0.75, 0.4)

# ── World background ──────────────────────────────────────────
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.015, 0.015, 0.02, 1)
bg.inputs[1].default_value = 0.05

# ── Camera ────────────────────────────────────────────────────
bpy.ops.object.camera_add(location=(12, -16, 10))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(58), 0, math.radians(38))
bpy.context.scene.camera = cam

# ── Animation: fragments drift and rotate ─────────────────────
for i, obj in enumerate(all_fragments):
    obj.animation_data_clear()
    phase = (i / len(all_fragments)) * math.pi * 2   # stagger phase

    bpy.context.scene.frame_set(1)
    obj.keyframe_insert("location")
    obj.keyframe_insert("rotation_euler")

    bpy.context.scene.frame_set(125)
    obj.location.z      += 1.0 + math.sin(phase) * 0.8
    obj.rotation_euler.z += math.pi + phase * 0.1
    obj.keyframe_insert("location")
    obj.keyframe_insert("rotation_euler")

    bpy.context.scene.frame_set(250)
    obj.location.z      -= 1.0 + math.sin(phase) * 0.8
    obj.rotation_euler.z += math.pi - phase * 0.1
    obj.keyframe_insert("location")
    obj.keyframe_insert("rotation_euler")

# ── Render settings ───────────────────────────────────────────
bpy.context.scene.render.engine       = "CYCLES"
bpy.context.scene.cycles.samples      = 64
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.frame_end           = 250
bpy.context.scene.render.fps          = 24

print("Done! Press F12 to render, Ctrl+F12 for animation.")
