import bpy
import bmesh
import math
from mathutils import Vector
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = REPO_ROOT / "design" / "blender_reactor" / "exports"


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.cycles.preview_samples = 16
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False
    scene.view_settings.look = "None"
    return scene


def make_material(name, base=(0.8, 0.8, 0.8, 1.0), emission=None, emission_strength=0.0, roughness=0.35, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Alpha"].default_value = alpha
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    if emission is not None and emission_strength > 0.0:
        add = nodes.new("ShaderNodeAddShader")
        emit = nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = emission
        emit.inputs["Strength"].default_value = emission_strength
        links.new(bsdf.outputs["BSDF"], add.inputs[0])
        links.new(emit.outputs["Emission"], add.inputs[1])
        links.new(add.outputs["Shader"], out.inputs["Surface"])

    if alpha < 1.0:
        mat.blend_method = "BLEND"
    return mat


def add_cylinder(name, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), material=None, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def add_uv_sphere(name, radius, location=(0, 0, 0), material=None, segments=48, ring_count=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def add_torus(name, major_radius, minor_radius, location=(0, 0, 0), rotation=(0, 0, 0), material=None, major_segments=48, minor_segments=18):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=major_segments,
        minor_segments=minor_segments,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def add_helix(name, radius, pitch, turns, thickness, phase=0.0, z0=0.0, z_scale=1.0, material=None, resolution=320):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = thickness
    curve.bevel_resolution = 6
    spline = curve.splines.new("POLY")
    spline.points.add(resolution - 1)
    z1 = z0 + turns * pitch * z_scale
    for i in range(resolution):
        t = i / (resolution - 1)
        theta = phase + turns * 2.0 * math.pi * t
        z = z0 + (z1 - z0) * t
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        spline.points[i].co = (x, y, z, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def add_trim_ring(name, radius, depth, z, material):
    return add_torus(name, radius, depth, location=(0, 0, z), rotation=(0, 0, 0), material=material)


def add_camera(name, location, rotation, lens=55):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = rotation
    return cam


def setup_world():
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links
    for node in list(nodes):
        nodes.remove(node)
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.03, 0.035, 0.045, 1.0)
    bg.inputs["Strength"].default_value = 0.8
    links.new(bg.outputs["Background"], out.inputs["Surface"])


def setup_lighting():
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 20))
    sun = bpy.context.object
    sun.data.energy = 2.5
    sun.rotation_euler = (math.radians(35), math.radians(0), math.radians(-20))

    bpy.ops.object.light_add(type="AREA", location=(18, -14, 8))
    area1 = bpy.context.object
    area1.data.energy = 6000
    area1.data.shape = "RECTANGLE"
    area1.data.size = 30
    area1.data.size_y = 20
    area1.rotation_euler = (math.radians(62), 0, math.radians(35))

    bpy.ops.object.light_add(type="AREA", location=(-16, 14, -5))
    area2 = bpy.context.object
    area2.data.energy = 3500
    area2.data.shape = "RECTANGLE"
    area2.data.size = 20
    area2.data.size_y = 16
    area2.rotation_euler = (math.radians(120), 0, math.radians(-140))


def create_scene():
    scene = reset_scene()
    setup_world()
    setup_lighting()

    # Materials
    m_structure = make_material("Structure", base=(0.11, 0.12, 0.14, 1.0), roughness=0.55)
    m_shell = make_material("Shell", base=(0.45, 0.48, 0.52, 1.0), roughness=0.25, alpha=0.18)
    m_plasma = make_material("Plasma", base=(0.08, 0.20, 0.35, 1.0), emission=(0.35, 0.75, 1.0, 1.0), emission_strength=18.0, roughness=0.1)
    m_axial = make_material("AxialCoils", base=(0.18, 0.25, 0.38, 1.0), emission=(0.12, 0.24, 0.5, 1.0), emission_strength=1.2, roughness=0.3)
    m_helix = make_material("HelixCoils", base=(0.15, 0.34, 0.22, 1.0), emission=(0.15, 0.55, 0.28, 1.0), emission_strength=1.0, roughness=0.3)
    m_trim = make_material("TrimCoils", base=(0.55, 0.24, 0.12, 1.0), emission=(0.85, 0.35, 0.08, 1.0), emission_strength=0.8, roughness=0.35)
    m_end = make_material("Endcaps", base=(0.75, 0.70, 0.62, 1.0), roughness=0.4)

    # Reactor scale in scene units
    L = 48.0
    chamber_r = 2.4
    shell_r = 3.0
    coil_r = 3.55
    plasma_r = 1.2

    # Main reactor body
    add_cylinder("VacuumShell", shell_r, L, material=m_shell)
    add_cylinder("PlasmaChannel", plasma_r, L * 0.96, material=m_plasma)
    add_cylinder("InnerStructure", chamber_r, L * 1.01, material=m_structure)

    # End treatment volumes
    for z in (-L * 0.5 - 3.0, L * 0.5 + 3.0):
        add_uv_sphere(f"EndCell_{z:.1f}", 2.8, location=(0, 0, z), material=m_end)
        add_cylinder(f"EndPlug_{z:.1f}", 1.6, 4.0, location=(0, 0, z), material=m_end)

    # Main axial coils: repeated circular rings
    axial_positions = [-18, -12, -6, 0, 6, 12, 18]
    for idx, z in enumerate(axial_positions):
        add_torus(f"AxialCoil_{idx}", coil_r, 0.18, location=(0, 0, z), rotation=(0, 0, 0), material=m_axial)

    # Helical shaping coils: two counterwound helices
    helix_turns = 7
    helix_pitch = L / helix_turns
    add_helix("HelixA", coil_r - 0.15, helix_pitch, helix_turns, 0.11, phase=0.0, z0=-L / 2, material=m_helix)
    add_helix("HelixB", coil_r - 0.15, helix_pitch, helix_turns, 0.11, phase=math.pi, z0=-L / 2, material=m_helix)

    # Trim coils: smaller modular correction rings
    trim_z = [-21, -15, -9, -3, 3, 9, 15, 21]
    for idx, z in enumerate(trim_z):
        add_trim_ring(f"Trim_{idx}", coil_r - 0.4, 0.09, z, m_trim)

    # Slight floor plane for visual reference
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -L * 0.52))
    floor = bpy.context.object
    floor.data.materials.append(m_structure)

    # Cameras for multiple exports
    cameras = [
        ("iso", (72, -62, 28), (math.radians(72), 0, math.radians(52))),
        ("side", (0, -90, 12), (math.radians(86), 0, 0)),
        ("end", (0, 0, 110), (0, 0, 0)),
        ("low", (82, -20, 6), (math.radians(84), 0, math.radians(80))),
    ]

    for name, loc, rot in cameras:
        add_camera(name, loc, rot, lens=45 if name != "end" else 60)

    scene.camera = bpy.data.objects["iso"]
    return scene


def render_views():
    scene = bpy.context.scene
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for cam_name in ["iso", "side", "end", "low"]:
        scene.camera = bpy.data.objects[cam_name]
        scene.render.filepath = str(EXPORT_DIR / f"{cam_name}.png")
        bpy.ops.render.render(write_still=True)


def main():
    create_scene()
    render_views()


if __name__ == "__main__":
    main()
