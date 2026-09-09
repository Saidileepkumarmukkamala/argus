"""Shared Blender scene setup for Notch Parade 3D clips. Run inside Blender (bpy).
World units = art px of the 184x52 canvas. X = along the strip (-92..92), Z = up (0 = floor), Y = depth (+Y = further back).
Camera: orthographic side view tilted 8 degrees down, so background lanes sit slightly higher on screen.
Renders to 552x156 (exactly 1 device px per render px on the notch at the 3x panel)."""
import bpy, math

ART_W, ART_H, SUP = 184, 52, 3
NOTCH_L, NOTCH_R, NOTCH_B = 31 - 92, 153 - 92, 52 - 21     # occluder in world X (-61..61) and its underside height (z=31)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'SceneEEVEE') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = ART_W * SUP, ART_H * SUP
    sc.render.resolution_percentage = 100
    sc.render.fps = 12
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('World'); sc.world = world; world.use_nodes = True
    bg = world.node_tree.nodes['Background']; bg.inputs[0].default_value = (0, 0, 0, 1); bg.inputs[1].default_value = 0.0
    return sc

def camera():
    cam_data = bpy.data.cameras.new('Cam'); cam_data.type = 'ORTHO'; cam_data.ortho_scale = ART_W
    cam = bpy.data.objects.new('Cam', cam_data); bpy.context.collection.objects.link(cam)
    cam.location = (0, -200, 50); cam.rotation_euler = (math.radians(82), 0, 0)
    bpy.context.scene.camera = cam
    return cam

def lights():
    def add(kind, name, loc, rot, energy, color=(1, 1, 1), size=None):
        d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
        if size and kind == 'AREA': d.size = size
        o = bpy.data.objects.new(name, d); bpy.context.collection.objects.link(o)
        o.location = loc; o.rotation_euler = rot; return o
    add('SUN', 'Key', (0, -80, 120), (math.radians(40), math.radians(-25), 0), 4.0, (1.0, 0.96, 0.9))
    add('SUN', 'Rim', (0, 120, 60), (math.radians(-60), math.radians(20), 0), 2.5, (0.6, 0.75, 1.0))
    add('AREA', 'Fill', (-60, -120, 30), (math.radians(70), 0, 0), 4000, (0.9, 0.95, 1.0), size=120)

def material(name, color, rough=0.4, metal=0.0, spec=0.5, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emit: p.inputs['Emission Color'].default_value = (*color, 1); p.inputs['Emission Strength'].default_value = emit
    return m

def rounded_box(name, size, loc, mat, bevel=1.5, parent=None, smooth=True):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    b = o.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 4
    if smooth:
        s = o.modifiers.new('sub', 'SUBSURF'); s.levels = 2; s.render_levels = 2
    o.data.materials.append(mat); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o

def sphere(name, r, loc, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12); o = bpy.context.object; o.name = name
    o.data.materials.append(mat); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o

def cylinder(name, r, depth, loc, rot, mat, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=32); o = bpy.context.object; o.name = name
    o.data.materials.append(mat); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o

def empty(name, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(o); o.location = loc; return o

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def render_frames(outdir, n, step):
    """step(frame_index) sets every transform for that frame; then we render it. Frame-by-frame = no interpolation surprises."""
    import os
    os.makedirs(outdir, exist_ok=True)
    sc = bpy.context.scene
    for i in range(n):
        step(i)
        sc.render.filepath = os.path.join(outdir, f'{i:04d}.png')
        bpy.ops.render.render(write_still=True)
