# Recipe specifications

The JSON specs drive the included generators. Dimensions are in **meters**.

## Detailed generator (`scripts/detail_asset.py`)

| Field | Allowed | Default |
|---|---|---|
| `type` | `precision_lens`, `studio_lamp` | required |
| `radius_m` | finite number 0.025–5 | 0.08 |
| `height_m` | finite number 0.025–5 | 0.18 |
| `detail_level` | `medium`, `high`, `ultra` | `high` |
| `render_samples` | integer 1–4096 | 48 |
| `render_resolution` | integer 256–8192 | 1024 |

The examples demonstrate approximate visual models rather than accurate replicas of any particular commercial product. Not intended for physically correct optical simulation or electrical/mechanical engineering. Objects are not automatically joined for print.

## Legacy generator (`scripts/build_asset.py`)

`type` of `stool`, `table`, `pedestal`, with width/depth/height in meters, `top_thickness` meters and `primary_color`/`accent_color` RGB lists. The legacy generator remains unchanged for compatibility.
