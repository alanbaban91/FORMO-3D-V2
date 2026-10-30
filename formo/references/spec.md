# FORMO — Starter JSON scene specification

The included Blender generator supports **stool**, **table**, and **pedestal** geometry. It is a code-driven example and is not a trained text-to-3D system.

| Key | Type | Notes |
| --- | --- | --- |
| `type` | string | `stool`, `table`, `pedestal` (required) |
| `width` | number | Width in meters, default 0.55 |
| `depth` | number | Depth in meters, defaults to width |
| `height` | number | Height in meters, default 0.7 |
| `top_thickness` | number | Slab/seat thickness in meters, default 0.05 |
| `primary_color` | [R,G,B] | Linear RGB color for tabletop/seat, 0–1 |
| `accent_color` | [R,G,B] | Linear RGB color for legs/support, 0–1 |

All dimensions should be positive. Geometry is designed for visualization, not guaranteed 3D-print-ready or optimized for a specific game engine. Preview renders use Blender Cycles and may require additional time. Exported GLBs contain the mesh assets and materials, not presentation lights/camera.

## Extending to arbitrary objects

Have the AI agent draft a new `bpy` script using the seven-step workflow in `SKILL.md`; organize the result into named components; validate topology; render; then export. The existing generator is an implementation example, not a hard limit on the agent's modeling capability.
