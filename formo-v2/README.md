# FORMO v2

**From words to forms.** An open-source AI agent skill and procedural Blender modeling toolkit for building **detailed, editable hard-surface 3D assets**.

FORMO helps an AI coding agent plan a model by components, generate geometry in Blender with Python, add construction details and materials, and export actual mesh files. The repository includes two substantial v2 recipes: a precision camera lens and an articulated studio lamp, plus the legacy simpler furniture generator.

> **Scope:** FORMO is an agent skill + executable procedural model recipes, **not** a pretrained, arbitrary text-to-3D foundation model. Creating an entirely different object requires the agent to author or adapt Blender Python. The shipped recipes have not been Blender-rendered in this environment, so results should be tested with your Blender version.

## What changed in v2

| Area | v1 | v2 |
|---|---|---|
| Example shapes | stool, table, pedestal | adds a mechanical lens and jointed lamp |
| Modeling | basic primitives | multi-component detail, grooves, fasteners, knurling, springs, optics |
| Config | dimensions and colors | meters, detail level, render controls |
| Outputs | BLEND + GLB + preview + report | same, detailed object hierarchy |
| Production workflows | introductory | expanded modeling and quality-gate guidance |

## Requirements

- Blender 4.x recommended (needs `bpy` and bundled glTF exporter)
- Python 3.10+ for optional local JSON/static tests
- No external Blender add-ons

## Generate a detailed 3D model

```bash
# High-detail procedural camera lens
blender --background --python scripts/detail_asset.py -- --spec examples/precision_lens.json --out output/lens

# Detailed articulated studio lamp, without rendering
blender --background --python scripts/detail_asset.py -- --spec examples/studio_lamp.json --out output/lamp --no-render
```

Outputs: `precision_lens.blend`, `precision_lens.glb`, `precision_lens_preview.png` (unless `--no-render`), `asset_report.json`; analogous files for `studio_lamp`.

For a faster / more detailed mesh, edit the `detail_level` field to `medium`, `high`, or `ultra`. Note that detail levels change certain counts of modeled subparts; they do **not** guarantee a target polygon count.

## Example brief to give an AI coding agent

> Use FORMO to create a detailed contemporary camera lens, 120 mm tall, with knurled focus ring, layered front optical elements, retaining rings, aperture markings, bayonet fasteners, and brushed metal surfaces. Keep parts named and editable. Generate a BLEND file, GLB and studio preview. Inspect results before claiming completion.

For objects beyond the two v2 recipes, the agent should design a dedicated Python model, following `SKILL.md` and `references/modeling-guide.md`.

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/detail_asset.py scripts/build_asset.py
```

These tests validate spec files and script syntax **without running Blender**. Blender execution, viewport inspection and export reimport are still necessary to validate actual 3D assets.

## Limitations

The v2 examples use material shader values rather than authored UV texture maps. They are deliberately multi-object assemblies with intersecting components and are not watertight/3D-print-ready. They are not retopologized, rigged, or optimized for real-time games. "Detailed" refers to more deliberate geometry and components, not universal photorealism.

## Repository

```
formo-v2/
├── SKILL.md
├── README.md
├── LICENSE
├── scripts/
│   ├── detail_asset.py
│   └── build_asset.py
├── examples/
│   ├── precision_lens.json
│   ├── studio_lamp.json
│   ├── stool.json
│   └── pedestal.json
├── references/
│   ├── spec.md
│   └── modeling-guide.md
└── tests/
    └── test_specs.py
```

## License

MIT. See `LICENSE`.
