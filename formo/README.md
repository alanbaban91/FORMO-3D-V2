# FORMO — AI 3D Modeling Skill for Blender

**From words to forms.**

A reusable **AI agent skill** for planning, modeling, surfacing, validating, and exporting 3D assets with Blender Python. Designed to live in a GitHub repository and be installed in agent environments that support `SKILL.md` skills.

> **Scope:** This is an instruction-based skill plus a working procedural Blender starter generator. It does **not** include a pretrained text-to-3D model or guarantee arbitrary objects can be generated from one JSON file.

## Structure

```text
formo/
├── SKILL.md                 # Agent instructions
├── README.md                # Installation & usage
├── LICENSE
├── .gitignore
├── examples/
│   ├── stool.json
│   └── pedestal.json
├── references/
│   └── spec.md
└── scripts/
    └── build_asset.py      # Blender Python implementation
```

## Install as a skill

Copy this folder to the skill directory of your AI coding agent, or point an agent that supports skill discovery at the directory containing `SKILL.md`. Skill discovery and activation rules vary across agents.

Example request to the agent:

> Use the FORMO skill to create a low-poly, mid-century wooden coffee table, 110 × 55 × 45 cm. Save an editable Blender file, export a GLB, and produce a preview. Report polygon count and any limitations.

The agent should write or adapt Blender code to match the brief, execute it where Blender is installed, and verify outputs.

## Run the provided examples

Requirements: **Blender 4.x or later** installed and available on your `PATH` (tested only by code inspection where Blender is unavailable).

```bash
blender --background --python scripts/build_asset.py -- --spec examples/stool.json --out output
```

To skip the preview render:

```bash
blender --background --python scripts/build_asset.py -- --spec examples/pedestal.json --out output --no-render
```

Creates: `stool.blend`, `stool.glb`, `stool_preview.png` (unless skipped), and `asset_report.json` in `output/`. These filenames vary by asset type.

## What the skill covers

- Reference-driven and brief-driven 3D modeling workflow
- Metric scale and clean component naming
- Procedural geometry and PBR material setup
- Basic mesh quality considerations
- Blender/GLB export and preview rendering
- Transparent reporting of limitations

## Roadmap

- Product modeling templates (packaging, bottles, electronics)
- Automated topology and manifold checks
- UV and texture pipeline
- Rigging and animation workflows
- LOD and game-engine export presets

## License

MIT — see [LICENSE](LICENSE).
