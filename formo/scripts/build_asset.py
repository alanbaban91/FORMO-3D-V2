"""Procedural Blender asset starter. Run with Blender, not system Python.

blender --background --python scripts/build_asset.py -- --spec examples/stool.json --out output
"""
import argparse
import json
import math
import sys
from pathlib import Path

try:
    import bpy
except ImportError as exc:
    raise SystemExit("This script requires Blender's Python (bpy). Run with blender --background --python ...") from exc


def arguments():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', required=True)
    parser.add_argument('--out', default='output')
    parser.add_argument('--no-render', action='store_true')
    return parser.parse_args(args)


def material(name, color, roughness=0.45, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1.0)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    return m


def cube(name, xyz, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new('Edge softening', 'BEVEL')
        mod.width = min(bevel, min(dims) * 0.4)
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def cylinder(name, xyz, radius, depth, mat, vertices=48, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=xyz)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new('Edge softening', 'BEVEL')
        mod.width = min(bevel, depth * 0.25, radius * 0.25)
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def create(spec):
    kind = spec['type']
    if kind not in ('stool', 'table', 'pedestal'):
        raise ValueError('type must be one of: stool, table, pedestal')
    width = float(spec.get('width', 0.55))
    depth = float(spec.get('depth', width))
    height = float(spec.get('height', 0.7))
    if not all(math.isfinite(v) and 0.08 <= v <= 20 for v in (width, depth, height)):
        raise ValueError('width, depth and height must be finite meters in [0.08, 20]')
    top_thickness = min(float(spec.get('top_thickness', 0.05)), height * .3)
    if not 0.005 <= top_thickness < height:
        raise ValueError('top_thickness must be positive and smaller than height')
    primary = material('Primary finish', spec.get('primary_color', [0.47, 0.27, 0.14]), 0.38)
    accent = material('Structural finish', spec.get('accent_color', [0.07, 0.08, 0.09]), 0.3, 0.65)
    top_z = height - top_thickness / 2
    if kind == 'stool':
        cylinder('Round seat', (0, 0, top_z), min(width, depth) / 2, top_thickness, primary, bevel=.012)
    else:
        cube('Top slab', (0, 0, top_z), (width, depth, top_thickness), primary, bevel=.012)
    leg_height = height - top_thickness
    if kind == 'pedestal':
        foot_width = width * .45
        cube('Central support', (0, 0, leg_height / 2), (foot_width, depth * .45, leg_height), accent, bevel=.012)
        cube('Foot plate', (0, 0, .018), (width * .85, depth * .85, .036), accent, bevel=.008)
    else:
        offset_x = width * .36
        offset_y = depth * .36
        thickness = min(width, depth) * .085
        for xname, x in [('L', -offset_x), ('R', offset_x)]:
            for yname, y in [('F', -offset_y), ('B', offset_y)]:
                cube(f'Leg {xname}{yname}', (x, y, leg_height / 2), (thickness, thickness, leg_height), accent, bevel=.006)
    return kind


def render_setup(height):
    world = bpy.context.scene.world
    world.color = (0.22, 0.22, 0.22)
    bpy.ops.object.camera_add(location=(2.2, -2.5, max(1.65, height * 2.3)))
    camera = bpy.context.object
    direction = (0, 0, height * .5)
    from mathutils import Vector
    camera.rotation_euler = (Vector(direction) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = camera
    bpy.ops.object.light_add(type='AREA', location=(1.5, -1.7, 3.0))
    bpy.context.object.data.energy = 550
    bpy.context.object.data.shape = 'DISK'
    bpy.context.object.data.size = 4.0
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100


def main():
    args = arguments()
    spec = json.loads(Path(args.spec).read_text(encoding='utf-8'))
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system = 'METRIC'
    kind = create(spec)
    assets = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not assets:
        raise RuntimeError('No asset meshes created')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in assets:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = assets[0]
    # Export before adding presentation-only camera and lights.
    glb = out / f'{kind}.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True)
    bpy.ops.object.select_all(action='DESELECT')
    render_setup(float(spec.get('height', .7)))
    blend = out / f'{kind}.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    png = None
    if not args.no_render:
        png = out / f'{kind}_preview.png'
        bpy.context.scene.render.filepath = str(png)
        bpy.ops.render.render(write_still=True)
    triangles = sum(sum(len(p.vertices) - 2 for p in obj.data.polygons) for obj in assets)
    report = {
        'type': kind,
        'dimensions_m': {k: float(spec.get(k, default)) for k, default in [('width', .55), ('depth', spec.get('width', .55)), ('height', .7)]},
        'objects': len(assets), 'base_mesh_triangles': triangles,
        'note': 'Base mesh triangle count excludes modifier-generated geometry.',
        'files': {'blend': str(blend), 'glb': str(glb), 'preview': str(png) if png else None}
    }
    (out / 'asset_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
