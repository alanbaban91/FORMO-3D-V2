"""FORMO v2: detailed procedural hard-surface Blender asset generator.

blender --background --python scripts/detail_asset.py -- --spec examples/precision_lens.json --out output/lens

Recipes: precision_lens, studio_lamp. Metric units. No external add-ons.
"""
import argparse
import json
import math
import sys
from pathlib import Path

try:
    import bpy
    from mathutils import Vector
except ImportError as exc:
    raise SystemExit('Run via Blender Python: blender --background --python scripts/detail_asset.py -- ...') from exc


def args_parse():
    cli = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--spec', required=True)
    p.add_argument('--out', default='output')
    p.add_argument('--no-render', action='store_true')
    return p.parse_args(cli)


def mat(name, rgb, rough=.4, metal=0, transmission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*rgb, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = transmission
    return m


def finish(obj, name, material, bevel=0, smooth=True):
    obj.name = name
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new('Micro edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def cylinder(name, radius, depth, z, material, verts=96, bevel=.0005, x=0, y=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=(x,y,z))
    return finish(bpy.context.object, name, material, bevel)


def torus(name, radius, minor, z, material, x=0, y=0):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=minor,
        major_segments=128, minor_segments=12, location=(x,y,z))
    return finish(bpy.context.object, name, material)


def block(name, dimensions, xyz, material, bevel=.001):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, material, bevel, smooth=False)


def sphere(name, size, xyz, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=xyz)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, material)


def rod(name, p1, p2, radius, material, verts=20):
    direction = Vector(p2) - Vector(p1)
    if direction.length < 1e-7:
        raise ValueError('Rod endpoints coincide')
    mid = (Vector(p1) + Vector(p2)) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=direction.length, location=mid)
    obj = bpy.context.object
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, material, radius*.2)


def lens(spec, materials):
    """Vertical upright lens with layered barrel, grips, fasteners and optical elements."""
    r = spec['radius_m']; h = spec['height_m']; detail = spec['detail_level']
    black, metal, rubber, glass, accent = [materials[k] for k in ('body','metal','rubber','glass','accent')]
    cylinder('01 Main barrel', r*.89, h*.83, h*.49, black, bevel=.0015)
    cylinder('02 Lower bayonet mount', r*.79, h*.085, h*.055, metal)
    cylinder('03 Mount gasket', r*.84, h*.024, h*.107, rubber)
    cylinder('04 Front retaining ring', r*.99, h*.07, h*.94, metal)
    cylinder('05 Front glass element', r*.80, h*.013, h*.977, glass, bevel=.001)
    cylinder('06 Inner optical shadow', r*.67, h*.002, h*.988, black, bevel=0)
    cylinder('07 Inner glass', r*.59, h*.005, h*.992, glass, bevel=0)
    for idx, f in enumerate((.18, .30, .68, .80, .895)):
        torus(f'Lathed accent channel {idx+1:02d}', r*.908, r*.018, h*f, metal)
    for idx, f in enumerate((.14,.16,.84,.86)):
        torus(f'Weather-seal groove {idx+1:02d}', r*.916, r*.012, h*f, rubber)
    # Knurled focus grip: many individual rounded raised radial bars.
    grip_count = {'medium':72, 'high':128, 'ultra':192}[detail]
    for i in range(grip_count):
        a = 2*math.pi*i/grip_count
        x,y = (r*.905*math.cos(a),r*.905*math.sin(a))
        obj = block(f'Focus grip ridge {i+1:03d}', (r*.025,r*.057,h*.26), (x,y,h*.48), rubber, bevel=r*.006)
        obj.rotation_euler.z = a + math.pi/2
    # Aperture ring markers and raised ticks.
    tick_count = 24 if detail == 'medium' else 48
    for i in range(tick_count):
        a = math.pi*2*i/tick_count
        obj = block(f'Aperture tick {i+1:02d}', (r*.018,r*.012,h*(.026 if i%4==0 else .012)),
            (r*.926*math.cos(a),r*.926*math.sin(a),h*.765), accent, bevel=r*.002)
        obj.rotation_euler.z = a
    # Six visible radial screw heads along mount / top ring.
    for i in range(8):
        a = 2*math.pi*i/8
        x,y = r*.69*math.cos(a),r*.69*math.sin(a)
        cylinder(f'Bayonet screw {i+1:02d}', r*.047, h*.009, h*.016, metal, verts=20, bevel=0, x=x,y=y)
        block(f'Screw slot {i+1:02d}', (r*.052,r*.007,h*.003), (x,y,h*.022),black,bevel=0)
    for i in range(12):
        a = i*2*math.pi/12
        x,y = r*.91*math.cos(a), r*.91*math.sin(a)
        sphere(f'Index bead {i+1:02d}', (r*.014,r*.014,r*.014), (x,y,h*.895),accent)
    return (2*r,h)


def lamp(spec, materials):
    """Articulated industrial desk lamp, with springs, pivots, ventilation and screws."""
    r=spec['radius_m']; h=spec['height_m']; detail=spec['detail_level']
    body,metal,rubber,glass,accent = [materials[k] for k in ('body','metal','rubber','glass','accent')]
    cylinder('01 Weighted base',r*.9,h*.055,h*.027,body,bevel=.004)
    cylinder('02 Base inset',r*.67,h*.009,h*.06,metal)
    cylinder('03 Main pivot collar',r*.20,h*.08,h*.10,metal)
    p0=(0,0,h*.11); p1=(0,0,h*.55); p2=(r*.87,0,h*.80)
    for k,dx in enumerate((-.035,.035)):
        rod(f'Lower arm rail {k+1}',(dx,0,p0[2]),(dx,0,p1[2]),r*.085,body)
        rod(f'Upper arm rail {k+1}',(dx,0,p1[2]),(p2[0]+dx,0,p2[2]),r*.074,body)
    for j,p in enumerate((p0,p1,p2)):
        sphere(f'Pivot hub {j+1}',(r*.22,r*.12,r*.22),p,metal)
        for s in (-1,1):
            rod(f'Pivot bolt {j+1} {s:+}',(p[0],s*r*.12,p[2]),(p[0],s*r*.16,p[2]),r*.06,accent)
    # Exposed tension springs along two arms.
    coils={'medium':18,'high':32,'ultra':48}[detail]
    for j,(a,b) in enumerate(((p0,p1),(p1,p2))):
        v=(Vector(b)-Vector(a)); axis=v.normalized()
        tangent=axis.cross(Vector((0,1,0))).normalized()
        for i in range(coils):
            t=i/(coils-1)
            center=Vector(a)+v*(.15+t*.7)+Vector((0,r*.16,0))
            phase=t*math.pi*2*(coils/5)
            pos=center+tangent*(r*.045*math.cos(phase))+Vector((0,r*.045*math.sin(phase),0))
            sphere(f'Spring {j+1} coil {i+1:02d}',(r*.018,)*3,pos,metal)
    # Lamp head angled downward; all parts clustered as a tiltable assembly.
    head=(p2[0]+r*.24,0,p2[2]-.06*h)
    sphere('Head hinge', (r*.17,r*.17,r*.17),head,metal)
    cylinder('Lamp shade shell',r*.52,h*.18,head[2]-.15*h,body,bevel=.003,x=head[0],y=head[1])
    cylinder('Reflector lip',r*.55,h*.022,head[2]-.245*h,metal,x=head[0],y=head[1])
    cylinder('Diffuser panel',r*.46,h*.008,head[2]-.258*h,glass,x=head[0],y=head[1])
    for i in range(18 if detail=='medium' else 36):
        a=2*math.pi*i/(18 if detail=='medium' else 36)
        obj=block(f'Head vent {i+1:02d}',(r*.028,r*.12,h*.012),
            (head[0]+r*.42*math.cos(a),r*.42*math.sin(a),head[2]-.10*h),rubber,bevel=.0005)
        obj.rotation_euler.z=a
    for i in range(8):
        a=2*math.pi*i/8
        cylinder(f'Diffuser fixing {i+1}',r*.022,h*.009,head[2]-.250*h,accent,verts=16,bevel=0,
                 x=head[0]+r*.49*math.cos(a),y=r*.49*math.sin(a))
    block('Power switch', (r*.27,r*.18,h*.045), (r*.34,0,h*.065),accent)
    return (r*2.8,h)


def make_studio(extent,h,spec):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=int(spec.get('render_samples',48))
    scene.render.resolution_x=int(spec.get('render_resolution',1024))
    scene.render.resolution_y=int(spec.get('render_resolution',1024))
    scene.render.resolution_percentage=100
    scene.world.color=(.18,.18,.18)
    bpy.ops.object.camera_add(location=(extent*2.5,-extent*3.2,h*1.8))
    camera=bpy.context.object
    target=Vector((0,0,h*.46))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'
    camera.data.ortho_scale=max(extent*2.6,h*1.4)
    scene.camera=camera
    for i,(loc,power,size) in enumerate((((-extent*2,-extent*2,h*2.3),650,extent*3),
                                         ((extent*2,extent,h*2),450,extent*2))):
        bpy.ops.object.light_add(type='AREA',location=loc)
        bpy.context.object.name=f'Studio light {i+1}'
        bpy.context.object.data.energy=power
        bpy.context.object.data.shape='DISK'
        bpy.context.object.data.size=max(size,.2)


def validate_spec(s):
    if s.get('type') not in ('precision_lens','studio_lamp'):
        raise ValueError('type must be precision_lens or studio_lamp')
    for key,default in [('radius_m',.08),('height_m',.18)]:
        value=float(s.get(key,default))
        if not math.isfinite(value) or not .025 <= value <= 5:
            raise ValueError(f'{key} must be finite meters in [0.025, 5]')
        s[key]=value
    if s.get('detail_level','high') not in ('medium','high','ultra'):
        raise ValueError('detail_level must be medium, high or ultra')
    s.setdefault('detail_level','high')
    for key,lo,hi in [('render_samples',1,4096),('render_resolution',256,8192)]:
        value=s.get(key,48 if key=='render_samples' else 1024)
        if not isinstance(value,int) or isinstance(value,bool) or not lo <= value <= hi:
            raise ValueError(f'{key} must be integer in [{lo},{hi}]')
    return s


def main():
    args=args_parse()
    spec=validate_spec(json.loads(Path(args.spec).read_text(encoding='utf-8')))
    out=Path(args.out).resolve(); out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system='METRIC'
    materials={
        'body':mat('Powder-coated aluminum',(.06,.067,.077),.32,.65),
        'metal':mat('Brushed machined steel',(.42,.45,.48),.24,.92),
        'rubber':mat('Fine-grain grip elastomer',(.02,.023,.029),.76,.0),
        'glass':mat('Optical glass',(.055,.10,.16),.08,.0,.45),
        'accent':mat('Engraving and fasteners',(.79,.57,.21),.34,.72)
    }
    dims=(lens(spec,materials) if spec['type']=='precision_lens' else lamp(spec,materials))
    assets=[o for o in bpy.context.scene.objects if o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for obj in assets: obj.select_set(True)
    bpy.context.view_layer.objects.active=assets[0]
    glb=out/(spec['type']+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
    bpy.ops.object.select_all(action='DESELECT')
    make_studio(dims[0],dims[1],spec)
    blend=out/(spec['type']+'.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    png=None
    if not args.no_render:
        png=out/(spec['type']+'_preview.png')
        bpy.context.scene.render.filepath=str(png)
        bpy.ops.render.render(write_still=True)
    report={
        'generator':'FORMO v2', 'recipe':spec['type'],'detail_level':spec['detail_level'],
        'mesh_objects':len(assets),'base_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in assets),
        'material_count':len(materials),'units':'meters',
        'warning':'Base polygon counts exclude modifiers. Assembly components overlap intentionally; not a watertight 3D-print model.',
        'files':{'blend':str(blend),'glb':str(glb),'preview':str(png) if png else None}
    }
    (out/'asset_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
