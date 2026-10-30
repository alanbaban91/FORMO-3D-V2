# Detailed modeling playbook

## Three-pass production approach

**Pass 1 — Construction:** Ground the primary silhouette and measured dimensions; break the object into realistic construction groups. Avoid details until the form reads correctly in silhouette.

**Pass 2 — Secondary forms:** Build collars, grooves, panels, mounts, housing transitions, material boundaries, joinery, fasteners, fittings, hinges, controls, vents, mechanical assemblies, and plausible seams. Use dimension-based parameters for spacing/size.

**Pass 3 — Finishing:** Bevel micro-edges, smooth or weight normals selectively, create surface microstructure via textures or modeled knurling, tune roughness and reflections, check overlaps and camera-facing details.

## Reference-led modeling

Treat images as approximate unless accompanied by measurements. Identify camera perspective and likely distortions. Confirm dimensions when accuracy is critical. For front/side views, measure proportions rather than copying arbitrary apparent sizes. Call out unknown back-side construction.

## Quality & realism

- Repeated elements must maintain consistent spacing and orientation.
- Assembly should show how parts attach or interact; avoid unsupported floating detail.
- Distinguish visually plausible geometry from mechanically functional design.
- For realistic renders, inspect black levels, edge highlights and glass transparency; add custom lights as needed.
- Add UVs, texture maps and wear only when the brief warrants them. Procedural shader colors alone are not authored textures.
- Export optimization, LOD generation, triangulation, normal bake and rigging are separate deliverables unless implemented.
- When inspecting `.glb`, reopening it in a clean scene can catch missing materials or improper transforms.

## Suggested future recipes

Headphones with drivers and stitched pads; typewriter with individual keys and mechanisms; industrial chair with stitching and hardware; camera body with control dials and lens mount; mechanical keyboard with stabilized keycaps and mounting plate; modular architectural panels.
